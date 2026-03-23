import { useState } from 'react'
import BillUpload from './components/BillUpload'
import BillList from './components/BillList'
import ChatPanel from './components/ChatPanel'

const TABS = ['Upload', 'Bills', 'Chat']

function loadBills() {
  try { return JSON.parse(localStorage.getItem('billsense_bills') || '[]') }
  catch { return [] }
}

export default function App() {
  const [tab, setTab] = useState('Upload')
  const [bills, setBills] = useState(loadBills)

  const addBill = (record) => {
    setBills((prev) => {
      const updated = [record, ...prev.filter((b) => b.bill_id !== record.bill_id)]
      localStorage.setItem('billsense_bills', JSON.stringify(updated))
      return updated
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🧾</span>
            <span className="text-xl font-bold text-gray-900">BillSense</span>
            <span className="hidden sm:inline text-sm text-gray-400 ml-1">AI Bill Processor</span>
          </div>
          <nav className="flex gap-1">
            {TABS.map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  tab === t
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {t}
                {t === 'Bills' && bills.length > 0 && (
                  <span className="ml-1.5 bg-indigo-600 text-white text-xs rounded-full px-1.5 py-0.5">
                    {bills.length}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Page content */}
      <main className="max-w-5xl mx-auto px-6 py-8">
        {tab === 'Upload' && <BillUpload onParsed={addBill} />}
        {tab === 'Bills'  && <BillList bills={bills} />}
        {tab === 'Chat'   && <ChatPanel />}
      </main>
    </div>
  )
}
