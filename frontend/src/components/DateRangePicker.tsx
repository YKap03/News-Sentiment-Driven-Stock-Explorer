interface DateRangePickerProps {
  startDate: string;
  endDate: string;
}

export default function DateRangePicker({
  startDate,
  endDate
}: DateRangePickerProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-1">
          Start Date
        </label>
        <input
          id="start-date"
          type="date"
          value={startDate}
          readOnly
          disabled
          className="w-full px-3 py-2 border border-gray-200 rounded-md shadow-sm bg-gray-100 text-gray-600 cursor-not-allowed"
        />
      </div>
      <div>
        <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 mb-1">
          End Date
        </label>
        <input
          id="end-date"
          type="date"
          value={endDate}
          readOnly
          disabled
          className="w-full px-3 py-2 border border-gray-200 rounded-md shadow-sm bg-gray-100 text-gray-600 cursor-not-allowed"
        />
      </div>
    </div>
  );
}

