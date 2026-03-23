import { useState } from 'react'
import { queryBill, exportBill } from '../api'

export default function BillInteract({ billId }) {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [exportMsg, setExportMsg] = useState(null)
  const [error, setError] = useState(null)

  const handleQuery = async () => {
    if (!question.trim()) return
    setLoading(true)
    setError(null)
    setAnswer(null)
    try {
      const res = await queryBill(billId, question)
      setAnswer(res.answer)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    setExporting(true)
    setExportMsg(null)
    setError(null)
    try {
      const res = await exportBill(billId)
      setExportMsg(`Saved → ${res.export_path}`)
    } catch (e) {
      setError(e.message)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-4">
      <h3 className="text-sm font-semibold text-gray-700">Ask About This Bill</h3>

      <div className="flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
          placeholder="e.g. What is the total amount? What did I buy?"
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        <button
          onClick={handleQuery}
          disabled={loading || !question.trim()}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {loading ? '…' : 'Ask'}
        </button>
      </div>

      {answer && (
        <div className="bg-indigo-50 border border-indigo-100 rounded-lg px-4 py-3 text-sm text-indigo-900">
          <span className="font-semibold">Answer: </span>{answer}
        </div>
      )}

      {error && (
        <p className="text-red-600 text-sm bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</p>
      )}

      <div className="border-t pt-3 flex items-center justify-between">
        <span className="text-xs text-gray-400 font-mono">ID: {billId}</span>
        <button
          onClick={handleExport}
          disabled={exporting}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50 transition-colors"
        >
          {exporting ? 'Exporting…' : '📁 Export JSON'}
        </button>
      </div>

      {exportMsg && (
        <p className="text-green-700 text-xs bg-green-50 border border-green-100 rounded-lg px-3 py-2">
          ✓ {exportMsg}
        </p>
      )}
    </div>
  )
}
