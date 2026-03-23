const fmt = (n, currency = '') =>
  n != null ? `${currency}${Number(n).toFixed(2)}` : '—'

export default function BillCard({ record }) {
  const { bill, parsed_at, source_file_name } = record

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      {/* Merchant + total */}
      <div className="flex items-start justify-between mb-5">
        <div>
          <h3 className="text-xl font-bold text-gray-900">
            {bill.merchant_name || 'Unknown Merchant'}
          </h3>
          {bill.merchant_address && (
            <p className="text-sm text-gray-500 mt-0.5">{bill.merchant_address}</p>
          )}
          {bill.merchant_phone && (
            <p className="text-sm text-gray-500">{bill.merchant_phone}</p>
          )}
        </div>
        <div className="text-right shrink-0 ml-4">
          <div className="text-3xl font-bold text-indigo-600">
            {fmt(bill.total, bill.currency || '$')}
          </div>
          {(bill.purchase_date || bill.purchase_time) && (
            <div className="text-xs text-gray-400 mt-0.5">
              {bill.purchase_date} {bill.purchase_time}
            </div>
          )}
        </div>
      </div>

      {/* Meta chips */}
      <div className="flex flex-wrap gap-2 mb-5">
        {[
          { label: 'Bill #', value: bill.bill_number },
          { label: 'Invoice #', value: bill.invoice_number },
          { label: 'Payment', value: bill.payment_method },
          { label: 'Source', value: source_file_name },
          { label: 'Parsed', value: new Date(parsed_at).toLocaleDateString() },
        ]
          .filter((m) => m.value)
          .map(({ label, value }) => (
            <span
              key={label}
              className="inline-flex items-center gap-1 bg-gray-100 text-gray-700 rounded-full px-3 py-1 text-xs"
            >
              <span className="text-gray-400">{label}</span>
              <span className="font-medium truncate max-w-[140px]">{value}</span>
            </span>
          ))}
      </div>

      {/* Items table */}
      {bill.items?.length > 0 && (
        <div className="mb-5">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Line Items</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-400 border-b border-gray-100">
                  <th className="pb-2 pr-4 font-medium">Description</th>
                  <th className="pb-2 pr-4 text-right font-medium">Qty</th>
                  <th className="pb-2 pr-4 text-right font-medium">Unit Price</th>
                  <th className="pb-2 text-right font-medium">Total</th>
                </tr>
              </thead>
              <tbody>
                {bill.items.map((item, i) => (
                  <tr key={i} className="border-b border-gray-50 last:border-0">
                    <td className="py-2 pr-4">{item.description || '—'}</td>
                    <td className="py-2 pr-4 text-right text-gray-600">{item.quantity ?? '—'}</td>
                    <td className="py-2 pr-4 text-right text-gray-600">
                      {item.unit_price != null ? fmt(item.unit_price) : '—'}
                    </td>
                    <td className="py-2 text-right font-medium">
                      {item.line_total != null ? fmt(item.line_total) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Totals summary */}
      <div className="border-t border-gray-100 pt-4 space-y-1.5 text-sm">
        {bill.subtotal  != null && (
          <div className="flex justify-between text-gray-600">
            <span>Subtotal</span><span>{fmt(bill.subtotal, bill.currency || '')}</span>
          </div>
        )}
        {bill.tax != null && (
          <div className="flex justify-between text-gray-600">
            <span>Tax</span><span>{fmt(bill.tax, bill.currency || '')}</span>
          </div>
        )}
        {bill.tax_breakdown?.length > 0 && (
          <div className="pt-1">
            <p className="text-xs text-gray-400 mb-1 font-medium uppercase tracking-wide">Tax Breakdown</p>
            <div className="space-y-1">
              {bill.tax_breakdown.map((tax, i) => {
                const labelParts = [tax.tax_type, tax.rate != null ? `(${tax.rate}%)` : null, tax.reference ? `on ${tax.reference}` : null]
                  .filter(Boolean)
                  .join(' ')
                return (
                  <div key={i} className="flex justify-between text-gray-600 text-sm">
                    <span>{labelParts || 'Tax component'}{tax.applies_to ? ` [${tax.applies_to}]` : ''}</span>
                    <span>{tax.amount != null ? fmt(tax.amount, bill.currency || '') : '—'}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}
        {bill.discount != null && (
          <div className="flex justify-between text-gray-600">
            <span>Discount</span><span>-{fmt(bill.discount, bill.currency || '')}</span>
          </div>
        )}
        {bill.total != null && (
          <div className="flex justify-between font-bold text-gray-900 text-base pt-1 border-t border-gray-100">
            <span>Total</span><span>{fmt(bill.total, bill.currency || '')}</span>
          </div>
        )}
      </div>

      {/* Notes */}
      {bill.notes?.length > 0 && (
        <div className="mt-4 pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-400 mb-1 font-medium uppercase tracking-wide">Notes</p>
          {bill.notes.map((n, i) => (
            <p key={i} className="text-sm text-gray-600">{n}</p>
          ))}
        </div>
      )}
    </div>
  )
}
