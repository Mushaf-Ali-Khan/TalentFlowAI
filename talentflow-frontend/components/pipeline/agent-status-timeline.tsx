'use client'

import { CheckCircle2, Circle, Loader2 } from 'lucide-react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export type StepStatus = 'pending' | 'active' | 'completed' | 'error'

interface Step {
  id: string
  title: string
  description: string
  status: StepStatus
}

export function AgentStatusTimeline({ steps }: { steps: Step[] }) {
  return (
    <div className="flow-root">
      <ul role="list" className="-mb-8">
        {steps.map((step, stepIdx) => (
          <li key={step.id}>
            <div className="relative pb-8">
              {stepIdx !== steps.length - 1 ? (
                <span
                  className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
                  aria-hidden="true"
                />
              ) : null}
              <div className="relative flex space-x-3">
                <div>
                  <span
                    className={cn(
                      'h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white',
                      step.status === 'completed' ? 'bg-green-500' : 
                      step.status === 'active' ? 'bg-blue-600' :
                      step.status === 'error' ? 'bg-red-500' : 'bg-gray-200'
                    )}
                  >
                    {step.status === 'completed' ? (
                      <CheckCircle2 className="h-5 w-5 text-white" aria-hidden="true" />
                    ) : step.status === 'active' ? (
                      <Loader2 className="h-5 w-5 text-white animate-spin" aria-hidden="true" />
                    ) : step.status === 'error' ? (
                      <span className="text-white text-xs font-bold">!</span>
                    ) : (
                      <Circle className="h-5 w-5 text-gray-400" aria-hidden="true" />
                    )}
                  </span>
                </div>
                <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{step.title}</p>
                    <p className="text-sm text-gray-500">{step.description}</p>
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
