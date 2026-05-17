'use client'

import { useState } from 'react'
import { MoreHorizontal, ShieldAlert, CheckCircle, XCircle } from 'lucide-react'

export interface CandidateRow {
  id: string
  name: string
  role: string
  total_score: number
  skills_match: number
  experience: number
  auto_rejected: boolean
  needs_manual_review: boolean
  status: string
}

export function CandidateTable({ candidates, onRowClick }: { candidates: CandidateRow[], onRowClick: (id: string) => void }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 shadow-sm bg-white">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Candidate</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Overall Score</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Skills</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Experience</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th scope="col" className="relative px-6 py-3"><span className="sr-only">Actions</span></th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {candidates.map((person) => (
            <tr key={person.id} onClick={() => onRowClick(person.id)} className="hover:bg-gray-50 cursor-pointer transition-colors">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <div className="h-10 w-10 flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center text-blue-700 font-semibold">
                      {person.name.charAt(0)}
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
                      {person.name}
                      {person.needs_manual_review && <ShieldAlert className="w-4 h-4 text-orange-500" title="Needs Manual Review" />}
                    </div>
                    <div className="text-sm text-gray-500">{person.role}</div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <div className="text-sm font-semibold text-gray-900">{person.total_score.toFixed(1)} / 100</div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="w-full bg-gray-200 rounded-full h-2 max-w-[100px]">
                  <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${person.skills_match * 10}%` }}></div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {person.experience.toFixed(1)} yrs
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {person.auto_rejected ? (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    <XCircle className="w-3 h-3 mr-1" /> Auto-Rejected
                  </span>
                ) : person.status === 'shortlisted' ? (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <CheckCircle className="w-3 h-3 mr-1" /> Shortlisted
                  </span>
                ) : (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    New
                  </span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button className="text-gray-400 hover:text-gray-600">
                  <MoreHorizontal className="w-5 h-5" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
