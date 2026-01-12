"use client"

import { useState, useMemo } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, ArrowUpDown } from "lucide-react"

interface DataTableProps {
  columns: string[]
  rows: Array<Record<string, any>>
}

export function DataTable({ columns, rows }: DataTableProps) {
  const [sortColumn, setSortColumn] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc")
  const [filterText, setFilterText] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const rowsPerPage = 20

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortColumn(column)
      setSortDirection("asc")
    }
  }

  const filteredAndSortedRows = useMemo(() => {
    let processed = [...rows]

    // Filter
    if (filterText) {
      const lowerFilter = filterText.toLowerCase()
      processed = processed.filter((row) =>
        Object.values(row).some((val) => String(val).toLowerCase().includes(lowerFilter)),
      )
    }

    // Sort
    if (sortColumn) {
      processed.sort((a, b) => {
        const aVal = a[sortColumn]
        const bVal = b[sortColumn]

        if (aVal === bVal) return 0

        const comparison = aVal < bVal ? -1 : 1
        return sortDirection === "asc" ? comparison : -comparison
      })
    }

    return processed
  }, [rows, filterText, sortColumn, sortDirection])

  const totalPages = Math.ceil(filteredAndSortedRows.length / rowsPerPage)
  const paginatedRows = filteredAndSortedRows.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage)

  return (
    <div className="space-y-3 h-full flex flex-col">
      <Input
        placeholder="Filter results..."
        value={filterText}
        onChange={(e) => {
          setFilterText(e.target.value)
          setCurrentPage(1)
        }}
        className="max-w-sm"
      />

      <div className="flex-1 overflow-auto border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((col) => (
                <TableHead key={col} className="whitespace-nowrap">
                  <button
                    onClick={() => handleSort(col)}
                    className="flex items-center gap-1 hover:text-foreground font-mono text-xs"
                  >
                    {col}
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedRows.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="text-center py-8 text-muted-foreground">
                  No results found
                </TableCell>
              </TableRow>
            ) : (
              paginatedRows.map((row, i) => (
                <TableRow key={i}>
                  {columns.map((col) => (
                    <TableCell key={col} className="font-mono text-xs whitespace-nowrap">
                      {row[col] != null ? String(row[col]) : "-"}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-xs text-muted-foreground">
            Page {currentPage} of {totalPages} ({filteredAndSortedRows.length} rows)
          </div>
          <div className="flex items-center gap-1">
            <Button variant="outline" size="sm" onClick={() => setCurrentPage(1)} disabled={currentPage === 1}>
              <ChevronsLeft className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage === totalPages}
            >
              <ChevronsRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
