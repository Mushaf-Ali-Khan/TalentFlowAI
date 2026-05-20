from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.agents.state import PipelineState

from app.agents.nodes.parser import ParserNode
from app.agents.nodes.extractor import ExtractorNode
from app.agents.nodes.embedder import EmbedderNode
from app.agents.nodes.matcher import MatcherNode
from app.agents.nodes.scorer import ScorerNode
from app.agents.nodes.bias_audit import BiasAuditNode
from app.agents.nodes.persist import PersistNode

def should_score_or_reject(state: PipelineState) -> str:
    # Only auto-reject if we actually computed a real semantic score AND it was below threshold.
    # semantic_score=0.0 means matching was skipped (no job embedding), so always score.
    if state.get('auto_rejected', False) and state.get('semantic_score', 0.0) > 0:
        return 'auto_reject'
    return 'score'

def create_pipeline_graph(checkpointer=None) -> CompiledStateGraph:
    builder = StateGraph(PipelineState)

    # Register nodes
    builder.add_node('parser', ParserNode())
    builder.add_node('extractor', ExtractorNode())
    builder.add_node('embedder', EmbedderNode())
    builder.add_node('matcher', MatcherNode())
    builder.add_node('scorer', ScorerNode())
    builder.add_node('bias_audit', BiasAuditNode())
    builder.add_node('persist', PersistNode())

    # Entry point
    builder.set_entry_point('parser')

    # Linear edges
    builder.add_edge('parser', 'extractor')
    builder.add_edge('extractor', 'embedder')
    builder.add_edge('embedder', 'matcher')

    # Conditional: skip scoring if auto-reject threshold
    builder.add_conditional_edges('matcher', should_score_or_reject, {
        'score': 'scorer',
        'auto_reject': 'bias_audit',  # Skip scoring, go to audit
    })

    builder.add_edge('scorer', 'bias_audit')
    builder.add_edge('bias_audit', 'persist')
    builder.add_edge('persist', END)

    if checkpointer:
        return builder.compile(checkpointer=checkpointer)
    else:
        return builder.compile()
