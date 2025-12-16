"use client"

import { useState, useEffect, useMemo } from "react"
import { Search, X, BookOpen } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

// base url based on env
// const baseUrl = process.env.NEXT_PUBLIC_BASE_URL ?? "http://127.0.0.1:8000";
const baseUrl =  "http://127.0.0.1:8000";

// return type for following endpoints:
// api/v1//search/name?q={name} 
// api/v1/search/research?q={research_interest}
// api/vi/search/all
type FacultyListItem = {
  id: number
  name: string
}

// return type for api/v1/faculty/{id} 
type FacultyDetail = {
  id: number
  name: string
  webpage_url: string
  research_interests: string
}

export default function FacultySearchPage() {
  // states for normal operation
  const [nameSearch, setNameSearch] = useState("")
  const [interestSearch, setInterestSearch] = useState("")
  const [results, setResults] = useState<FacultyListItem[]>([]) // [{id, name}]
  const [selectedFaculty, setSelectedFaculty] = useState<FacultyDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [debounceTimer, setDebounceTimer] = useState<NodeJS.Timeout | null>(null)
  const [allFaculty, setAllFaculty] = useState<FacultyListItem[] | null>(null)

  // states for admin hadnling
  const [adminOpen, setAdminOpen] = useState(false)
  const [adminUser, setAdminUser] = useState("")
  const [adminPass, setAdminPass] = useState("")
  const [updateLoading, setUpdateLoading] = useState(false)
  const [updateMessage, setUpdateMessage] = useState("")

  // debounce helper to not spam the backend
  const debounce = (fn: () => void) => {
    if (debounceTimer) clearTimeout(debounceTimer)
    const t = setTimeout(fn, 250)
    setDebounceTimer(t)
  }
  // setTimeout: wait before executing osme funciton
  // clearTimeout: cancels an established timeout

  // populate faculty cache on mount
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${baseUrl}/api/v1/search/all`)
        if (res.ok) {
          const data: FacultyListItem[] = await res.json()
          setAllFaculty(data)
        }
      } catch (_) {}
    })()
  }, [])

  // trigger search from name or interest
  useEffect(() => {
    const noQuery = nameSearch.trim() === "" && interestSearch.trim() === ""

    if (noQuery) {
      if (debounceTimer) clearTimeout(debounceTimer)
      if (allFaculty) setResults(allFaculty)
      else setResults([])
      return
    }

    debounce(async () => {
      setLoading(true)

      // choose endpoint
      let url = ""
      // encodeURIComponent is a js function that makes it safe to turn strings into safe url inputs
      if (nameSearch) url = `${baseUrl}/api/v1/search/name?q=${encodeURIComponent(nameSearch)}`
      else url = `${baseUrl}/api/v1/search/research?q=${encodeURIComponent(interestSearch)}`

      try {
        const res = await fetch(url)
        const data = await res.json()
        setResults(data) // data = [{id, name}]
      } catch (_) {
        setResults([])
      }

      setLoading(false)
    })
  }, [nameSearch, interestSearch, allFaculty])

  useEffect(() => {
    if (results.length !== 1) return

    const only = results[0]

    // do not refetch if already selected
    if (selectedFaculty && selectedFaculty.id === only.id) return
      ; (async () => {
        try {
          const res = await fetch(`${baseUrl}/api/v1/faculty/${only.id}`)
          const data: FacultyDetail = await res.json()
          setSelectedFaculty(data)
        } catch (_) {
          setSelectedFaculty(null)
        }
      })()
  }, [results])

  const clearFilters = () => {
    setNameSearch("")
    setInterestSearch("")
    setResults([])
  }

  // handles selection of a faculty name
  const handleSelect = async (id: number) => {
    try {
      const res = await fetch(`${baseUrl}/api/v1/faculty/${id}`)
      const data = await res.json() // full detail
      setSelectedFaculty(data)
    } catch (_) {
      setSelectedFaculty(null)
    }
  }

  // handle update button
  const handleUpdate = async () => {
    if (!adminUser || !adminPass) return
    setUpdateLoading(true)
    setUpdateMessage("")

    try {
      const res = await fetch(`${baseUrl}/api/v1/update`, {
        method: "POST",
        headers: {
          "Authorization": "Basic " + btoa(`${adminUser}:${adminPass}`)
        }
      })
      const data = await res.json()
      if (res.ok) {
        // update faculty on update
        setAllFaculty(null)
        const r = await fetch(`${baseUrl}/api/v1/faculty/all`)
        if (r.ok) setAllFaculty(await r.json())

        setUpdateMessage(`Success: ${data.record_count} records updated`)
      } else {
        setUpdateMessage(`Error: ${data.detail || "Unknown error"}`)
      }
    } catch (e) {
      setUpdateMessage(`Error: ${e}`)
    }
    setUpdateLoading(false)
  }

  return (
    <div className="min-h-screen relative overflow-hidden">

      {/* --- Purdue gold / cream fairylike background (inserted) --- */}
      <div className="fixed inset-0 -z-10">
        {/* soft gold/cream gradient */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(135deg, #fffaf0 0%, #fff3d6 40%, #f6e7b8 100%)",
          }}
        />
      </div>
      {/* --- end background --- */}

      <div className="container mx-auto px-4 py-8 max-w-7xl">



        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-[hsl(0,0%,13%)] mb-2 tracking-tight">Purdue ECE Faculty Directory</h1>
          <p className="text-sm text-muted-foreground">Search by name or research interests</p>
        </header>

        <div className="glass rounded-2xl p-6 mb-6 shadow-xl">

          <div className="grid md:grid-cols-2 gap-4 mb-4">

            <div className="space-y-2">
              <label htmlFor="name-search" className="text-sm font-medium text-foreground block">Search by Name</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="name-search"
                  type="text"
                  placeholder="Enter faculty name..."
                  value={nameSearch}
                  onChange={(e) => setNameSearch(e.target.value)}
                  className="pl-10 text-sm glass border-input/50 focus:border-primary"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="interest-search" className="text-sm font-medium text-foreground block">Search by Research Interest</label>
              <div className="relative">
                <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="interest-search"
                  type="text"
                  placeholder="Enter research area..."
                  value={interestSearch}
                  onChange={(e) => setInterestSearch(e.target.value)}
                  className="pl-10 text-sm glass border-input/50 focus:border-primary"
                />
              </div>
            </div>



          </div>
          {/* Admin Update Section */}
          <Button className="mb-4" variant="outline" onClick={() => setAdminOpen(!adminOpen)}>
            {adminOpen ? "Close Admin Panel" : "Admin Update"}
          </Button>

          {adminOpen && (
            <div className="mt-0 space-y-2">
              <Input
                type="text"
                placeholder="Username"
                value={adminUser}
                onChange={(e) => setAdminUser(e.target.value)}
                className="mb-4"
              />
              <Input
                type="password"
                placeholder="Password"
                value={adminPass}
                onChange={(e) => setAdminPass(e.target.value)}
                className="mb-4"
              />
              <Button onClick={handleUpdate} disabled={updateLoading}>
                {updateLoading ? "Updating..." : "Run Update"}
              </Button>
              {updateMessage && <p className="text-sm mt-2">{updateMessage}</p>}
            </div>
          )}
          <br></br>

          {(nameSearch || interestSearch) && (
            <div className="flex items-center justify-between pt-3 border-t border-border/50">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs text-muted-foreground">Active filters:</span>
                {nameSearch && (<Badge variant="secondary" className="text-xs">Name: {nameSearch}</Badge>)}
                {interestSearch && (<Badge variant="secondary" className="text-xs">Interest: {interestSearch}</Badge>)}
              </div>
              <Button variant="ghost" size="sm" onClick={clearFilters} className="text-xs h-7">
                <X className="h-3 w-3 mr-1" />
                Clear
              </Button>
            </div>
          )}
        </div>

        <div className="mb-4">
          <p className="text-xs text-muted-foreground">
            Showing {results.length} faculty
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((f) => (
            <button
              key={f.id}
              onClick={() => handleSelect(f.id)}
              className="glass rounded-xl p-5 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02] text-left group border border-border/50 hover:border-primary/30"
            >
              <div className="flex items-start gap-4 mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-foreground mb-0.5 truncate group-hover:text-primary transition-colors">
                    {f.name}
                  </h3>
                  <p className="text-xs text-muted-foreground">Click to open</p>
                </div>
              </div>
            </button>
          ))}
        </div>

        {loading && (
          <div className="text-center mt-4 text-xs text-muted-foreground">Loading...</div>
        )}

        {results.length === 0 && !loading && (nameSearch || interestSearch) && (
          <div className="glass rounded-xl p-12 text-center">
            <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-50" />
            <h3 className="text-base font-semibold text-foreground mb-2">No faculty found</h3>
            <p className="text-sm text-muted-foreground mb-4">Try adjusting your search criteria</p>
            <Button onClick={clearFilters} variant="outline" size="sm" className="text-xs bg-transparent">
              Clear Filters
            </Button>
          </div>
        )}

        {selectedFaculty && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl p-6 w-full max-w-lg">
              <h2 className="text-lg font-semibold mb-2">{selectedFaculty.name}</h2>
              <br></br>
              <h3 className="text-sm font-semibold mb-2">Personal Webpage:</h3>
              {/* target='_blank' means open in new tab */}
              <p className="text-sm mb-2">
                {/* rel='noopener noreferrer' means browser wont send http referer header to target website */}
                {selectedFaculty.webpage_url ? (
                  <a href={selectedFaculty.webpage_url} target="_blank" rel="noopener noreferrer">
                    <u>{selectedFaculty.webpage_url}</u>
                  </a>
                ) : (
                  "N/A"
                )}
              </p>
              <br></br>
              <h3 className="text-sm font-semibold mb-2">Research Interests:</h3>
              <p className="text-sm">
                {selectedFaculty.research_interests ? (
                  selectedFaculty.research_interests
                ) : (
                  "N/A"
                )}
              </p>
              <br></br>
              <Button onClick={() => setSelectedFaculty(null)} className="mt-4">Close</Button>
            </div>
          </div>
        )}

      </div>


    </div>
  )
}