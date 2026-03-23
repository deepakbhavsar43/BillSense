import { useState } from 'react'
import BillCard from './BillCard'
import BillInteract from './BillInteract'

export default function BillList({ bills }) {
  const [expanded, setExpanded] = useState(null)

  if (bills.length === 0) {
    return (
      <div className="text-center py-20 text-gray-400">
        <div className="text-6xl mb-4">🧾</div>
        <p className="text-lg font-medium text-gray-500">No bills yet</p>
        <p className="text-sm mt-1">Upload a bill in the <strong>Upload</strong> tab to get started.</p>
      </div>
    )
  }

  const toggle = (id) => setExpanded((prev) => (prev === id ? null : id))

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold text-gray-900">
        Parsed Bills{' '}
        <span className="text-gray-400 font-normal text-sm">({bills.length})</span>
      </h2>

      {bills.map((record) => {
        const open = expanded === record.bill_id
        return (
          <div
            key={record.bill_id}
            className="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm"
          >
            {/* Row header */}
            <button
              onClick={() => toggle(record.bill_id)}
              className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors text-left"
            >
              <div className="min-w-0">
                <div className="font-semibold text-gray-900 truncate">
                  {record.bill.merchant_name || 'Unknown Merchant'}
                </div>
                <div className="text-xs text-gray-400 mt-0.5 truncate">
                  {record.bill.purchase_date || new Date(record.parsed_at).toLocaleDateString()}
                  {' · '}
                  {record.source_file_name}
                </div>
              </div>
              <div className="flex items-center gap-3 ml-4 shrink-0">
                {record.bill.total != null && (
                  <span className="font-bold text-indigo-600 text-lg">
                    {record.bill.currency || '$'}
                    {Number(record.bill.total).toFixed(2)}
                  </span>
                )}
                <span className="text-gray-400 text-xs">{open ? '▲' : '▼'}</span>
              </div>
            </button>

            {/* Expanded details */}
            {open && (
              <div className="border-t border-gray-100 bg-gray-50 p-4 space-y-3">
                <BillCard record={record} />
                <BillInteract billId={record.bill_id} />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
