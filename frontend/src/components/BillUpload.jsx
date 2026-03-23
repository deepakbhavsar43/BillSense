import { useState } from 'react'
import { parseBill } from '../api'
import BillCard from './BillCard'
import BillInteract from './BillInteract'

export default function BillUpload({ onParsed }) {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [record, setRecord] = useState(null)
  const [error, setError] = useState(null)
  const [dragging, setDragging] = useState(false)

  const handleFile = (f) => {
    if (!f) return
    if (!f.type.startsWith('image/')) { setError('Please select an image file.'); return }
    setFile(f)
    setError(null)
    setRecord(null)
    const reader = new FileReader()
    reader.onload = (e) => setPreview(e.target.result)
    reader.readAsDataURL(f)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  const handleSubmit = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const result = await parseBill(file)
      setRecord(result)
      onParsed?.(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Upload a Bill</h2>
        <p className="text-sm text-gray-500 mt-1">
          Drop a bill or receipt image — BillSense will extract every field automatically using Gemini.
        </p>
      </div>

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onClick={() => document.getElementById('bill-file-input').click()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
          dragging
            ? 'border-indigo-400 bg-indigo-50'
            : 'border-gray-300 hover:border-indigo-400 hover:bg-gray-50'
        }`}
      >
        <input
          id="bill-file-input"
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {preview ? (
          <img
            src={preview}
            alt="Bill preview"
            className="max-h-56 mx-auto rounded-lg object-contain shadow"
          />
        ) : (
          <>
            <div className="text-5xl mb-3">📸</div>
            <p className="text-gray-600 font-medium">Drop a bill image here or click to select</p>
            <p className="text-sm text-gray-400 mt-1">JPG, PNG, WEBP, HEIC supported</p>
          </>
        )}
        {file && <p className="text-sm text-indigo-600 mt-3 font-medium">{file.name}</p>}
      </div>

      {error && (
        <p className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg px-4 py-2">
          {error}
        </p>
      )}

      <button
        onClick={handleSubmit}
        disabled={!file || loading}
        className="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Analyzing with Gemini…
          </>
        ) : (
          '🔍 Analyze Bill'
        )}
      </button>

      {record && (
        <div className="space-y-4">
          <BillCard record={record} />
          <BillInteract billId={record.bill_id} />
        </div>
      )}
    </div>
  )
}
