import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Plus, X, RotateCcw, Download, Upload, Trash2 } from 'lucide-react';

interface Person {
  id: string;
  name: string;
  x: number;
  y: number;
  dateAdded: string;
  quadrant: string;
  lastMoved: string;
}

interface SaveData {
  metadata: {
    lastUpdated: string;
    totalPeople: number;
    version: string;
  };
  people: Record<string, Omit<Person, 'id'>>;
}

const PersonalityCompass: React.FC = () => {
  const [people, setPeople] = useState<Person[]>([]);
  const [newPersonName, setNewPersonName] = useState('');
  const [draggedPerson, setDraggedPerson] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [selectedPerson, setSelectedPerson] = useState<string | null>(null);
  const gridRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Quadrant determination
  const getQuadrant = useCallback((x: number, y: number): string => {
    if (x >= 0 && y >= 0) return "Gnatty NPC";
    if (x < 0 && y >= 0) return "Not NPC";
    if (x < 0 && y < 0) return "Not Non-NPC";
    return "Gnatty Non-NPC";
  }, []);

  // Convert grid coordinates to percentages
  const coordsToPercent = useCallback((x: number, y: number) => ({
    x: ((x + 100) / 200) * 100,
    y: ((100 - y) / 200) * 100 // Invert Y for CSS positioning
  }), []);

  // Convert percentages to grid coordinates
  const percentToCoords = useCallback((percentX: number, percentY: number) => ({
    x: (percentX / 100) * 200 - 100,
    y: 100 - (percentY / 100) * 200 // Invert Y for CSS positioning
  }), []);

  // Save data to localStorage
  const saveData = useCallback((updatedPeople: Person[]) => {
    const saveData: SaveData = {
      metadata: {
        lastUpdated: new Date().toISOString(),
        totalPeople: updatedPeople.length,
        version: "2.0"
      },
      people: {}
    };

    updatedPeople.forEach(person => {
      saveData.people[person.name] = {
        name: person.name,
        x: person.x,
        y: person.y,
        dateAdded: person.dateAdded,
        quadrant: person.quadrant,
        lastMoved: person.lastMoved
      };
    });

    localStorage.setItem('personalityCompassData', JSON.stringify(saveData));
  }, []);

  // Load data from localStorage
  const loadData = useCallback(() => {
    try {
      const savedData = localStorage.getItem('personalityCompassData');
      if (savedData) {
        const parsed: SaveData = JSON.parse(savedData);
        const loadedPeople: Person[] = Object.entries(parsed.people || parsed as any).map(([name, data]) => ({
          id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
          name,
          x: data.x,
          y: data.y,
          dateAdded: data.dateAdded || new Date().toISOString(),
          quadrant: data.quadrant || getQuadrant(data.x, data.y),
          lastMoved: data.lastMoved || new Date().toISOString()
        }));
        setPeople(loadedPeople);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  }, [getQuadrant]);

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Add new person
  const addPerson = useCallback(() => {
    if (!newPersonName.trim()) return;
    
    if (people.some(p => p.name === newPersonName.trim())) {
      alert(`${newPersonName.trim()} is already on the grid.`);
      return;
    }

    const now = new Date().toISOString();
    const newPerson: Person = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      name: newPersonName.trim(),
      x: 0,
      y: 0,
      dateAdded: now,
      quadrant: getQuadrant(0, 0),
      lastMoved: now
    };

    const updatedPeople = [...people, newPerson];
    setPeople(updatedPeople);
    saveData(updatedPeople);
    setNewPersonName('');
  }, [newPersonName, people, getQuadrant, saveData]);

  // Remove person
  const removePerson = useCallback((id: string) => {
    const updatedPeople = people.filter(p => p.id !== id);
    setPeople(updatedPeople);
    saveData(updatedPeople);
    if (selectedPerson === id) setSelectedPerson(null);
  }, [people, saveData, selectedPerson]);

  // Clear all people
  const clearAll = useCallback(() => {
    if (window.confirm('Clear all people from the grid?')) {
      setPeople([]);
      saveData([]);
      setSelectedPerson(null);
    }
  }, [saveData]);

  // Handle mouse/touch events for dragging
  const handlePointerDown = useCallback((e: React.PointerEvent, person: Person) => {
    e.preventDefault();
    if (!gridRef.current) return;

    const rect = gridRef.current.getBoundingClientRect();
    const { x: percentX, y: percentY } = coordsToPercent(person.x, person.y);
    const actualX = (percentX / 100) * rect.width;
    const actualY = (percentY / 100) * rect.height;

    setDraggedPerson(person.id);
    setDragOffset({
      x: e.clientX - rect.left - actualX,
      y: e.clientY - rect.top - actualY
    });
    setSelectedPerson(person.id);
  }, [coordsToPercent]);

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    if (!draggedPerson || !gridRef.current) return;

    const rect = gridRef.current.getBoundingClientRect();
    const percentX = Math.max(0, Math.min(100, ((e.clientX - rect.left - dragOffset.x) / rect.width) * 100));
    const percentY = Math.max(0, Math.min(100, ((e.clientY - rect.top - dragOffset.y) / rect.height) * 100));
    
    const { x, y } = percentToCoords(percentX, percentY);
    
    const updatedPeople = people.map(p =>
      p.id === draggedPerson
        ? { ...p, x, y, quadrant: getQuadrant(x, y), lastMoved: new Date().toISOString() }
        : p
    );
    
    setPeople(updatedPeople);
  }, [draggedPerson, dragOffset, people, getQuadrant, percentToCoords]);

  const handlePointerUp = useCallback(() => {
    if (draggedPerson) {
      saveData(people);
    }
    setDraggedPerson(null);
    setDragOffset({ x: 0, y: 0 });
  }, [draggedPerson, people, saveData]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setDraggedPerson(null);
        setDragOffset({ x: 0, y: 0 });
      } else if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedPerson) {
          removePerson(selectedPerson);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedPerson, removePerson]);

  // Export data
  const exportData = useCallback(() => {
    const saveData: SaveData = {
      metadata: {
        lastUpdated: new Date().toISOString(),
        totalPeople: people.length,
        version: "2.0"
      },
      people: {}
    };

    people.forEach(person => {
      saveData.people[person.name] = {
        name: person.name,
        x: person.x,
        y: person.y,
        dateAdded: person.dateAdded,
        quadrant: person.quadrant,
        lastMoved: person.lastMoved
      };
    });

    const blob = new Blob([JSON.stringify(saveData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `personality_compass_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [people]);

  // Import data
  const importData = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target?.result as string);
        const loadedPeople: Person[] = Object.entries(data.people || data).map(([name, personData]: [string, any]) => ({
          id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
          name,
          x: personData.x,
          y: personData.y,
          dateAdded: personData.dateAdded || new Date().toISOString(),
          quadrant: personData.quadrant || getQuadrant(personData.x, personData.y),
          lastMoved: personData.lastMoved || new Date().toISOString()
        }));
        setPeople(loadedPeople);
        saveData(loadedPeople);
      } catch (error) {
        alert('Error importing file. Please check the file format.');
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  }, [getQuadrant, saveData]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold text-slate-800 mb-2">Personality Compass</h1>
          <p className="text-slate-600">Map your friends across the personality dimensions</p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex gap-3 items-center">
              <input
                type="text"
                value={newPersonName}
                onChange={(e) => setNewPersonName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addPerson()}
                placeholder="Enter person's name..."
                className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              />
              <button
                onClick={addPerson}
                className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Plus size={16} />
                Add Person
              </button>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={exportData}
                className="bg-green-500 hover:bg-green-600 text-white px-3 py-2 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Download size={16} />
                Export
              </button>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="bg-purple-500 hover:bg-purple-600 text-white px-3 py-2 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Upload size={16} />
                Import
              </button>
              <button
                onClick={clearAll}
                className="bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Trash2 size={16} />
                Clear All
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* People List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 h-fit">
              <h3 className="text-lg font-semibold text-slate-800 mb-4">People ({people.length})</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {people.map((person) => (
                  <div
                    key={person.id}
                    onClick={() => setSelectedPerson(person.id)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedPerson === person.id
                        ? 'bg-blue-100 border border-blue-300'
                        : 'bg-slate-50 hover:bg-slate-100'
                    }`}
                  >
                    <div className="font-medium text-slate-800">{person.name}</div>
                    <div className="text-xs text-slate-500">
                      ({person.x.toFixed(0)}, {person.y.toFixed(0)})
                    </div>
                    <div className="text-xs text-slate-500">{person.quadrant}</div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        removePerson(person.id);
                      }}
                      className="mt-2 text-red-500 hover:text-red-700 text-xs"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Instructions */}
            <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
              <h3 className="text-lg font-semibold text-slate-800 mb-4">Instructions</h3>
              <div className="text-sm text-slate-600 space-y-2">
                <div>
                  <strong>Keyboard Shortcuts:</strong>
                  <ul className="ml-4 mt-1 space-y-1">
                    <li>• Enter: Add person</li>
                    <li>• Delete: Remove selected</li>
                    <li>• Escape: Cancel drag</li>
                  </ul>
                </div>
                <div>
                  <strong>Mouse Controls:</strong>
                  <ul className="ml-4 mt-1 space-y-1">
                    <li>• Drag: Move person</li>
                    <li>• Click: Select person</li>
                  </ul>
                </div>
                <div>
                  <strong>Axes:</strong>
                  <ul className="ml-4 mt-1 space-y-1">
                    <li>• X: Not (-100) → Gnatty (+100)</li>
                    <li>• Y: Non NPC (-100) → NPC (+100)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Grid */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div
                ref={gridRef}
                className="relative w-full h-96 lg:h-[600px] border-2 border-slate-300 rounded-lg overflow-hidden cursor-crosshair"
                onPointerMove={handlePointerMove}
                onPointerUp={handlePointerUp}
                onPointerLeave={handlePointerUp}
              >
                {/* Grid Lines */}
                <div className="absolute inset-0 pointer-events-none">
                  {/* Vertical lines */}
                  {[0, 25, 50, 75, 100].map(x => (
                    <div
                      key={`v${x}`}
                      className={`absolute h-full ${x === 50 ? 'border-l-2 border-slate-400' : 'border-l border-slate-200'}`}
                      style={{ left: `${x}%` }}
                    />
                  ))}
                  {/* Horizontal lines */}
                  {[0, 25, 50, 75, 100].map(y => (
                    <div
                      key={`h${y}`}
                      className={`absolute w-full ${y === 50 ? 'border-t-2 border-slate-400' : 'border-t border-slate-200'}`}
                      style={{ top: `${y}%` }}
                    />
                  ))}
                </div>

                {/* Quadrant Labels */}
                <div className="absolute top-2 right-2 bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                  Gnatty NPC
                </div>
                <div className="absolute top-2 left-2 bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-medium">
                  Not NPC
                </div>
                <div className="absolute bottom-2 left-2 bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                  Not Non-NPC
                </div>
                <div className="absolute bottom-2 right-2 bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs font-medium">
                  Gnatty Non-NPC
                </div>

                {/* Axis Labels */}
                <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full mt-2 text-sm font-medium text-slate-700">
                  Not ← → Gnatty
                </div>
                <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-full -rotate-90 mr-2 text-sm font-medium text-slate-700">
                  Non NPC ← → NPC
                </div>

                {/* People */}
                {people.map((person) => {
                  const { x: percentX, y: percentY } = coordsToPercent(person.x, person.y);
                  const isSelected = selectedPerson === person.id;
                  const isDragging = draggedPerson === person.id;

                  return (
                    <div
                      key={person.id}
                      className={`absolute transform -translate-x-1/2 -translate-y-1/2 cursor-move select-none ${
                        isDragging ? 'z-50' : 'z-10'
                      }`}
                      style={{
                        left: `${percentX}%`,
                        top: `${percentY}%`,
                      }}
                      onPointerDown={(e) => handlePointerDown(e, person)}
                    >
                      <div
                        className={`w-4 h-4 rounded-full transition-all ${
                          isSelected
                            ? 'bg-blue-500 ring-4 ring-blue-200'
                            : 'bg-red-500 hover:bg-red-600'
                        } ${isDragging ? 'scale-125 shadow-lg' : 'shadow-md'}`}
                      />
                      <div
                        className={`absolute left-full top-0 ml-2 px-2 py-1 rounded text-xs font-medium whitespace-nowrap transition-all ${
                          isSelected
                            ? 'bg-blue-500 text-white'
                            : 'bg-white text-slate-800 border border-slate-300'
                        } ${isDragging ? 'shadow-lg' : 'shadow-sm'}`}
                      >
                        {person.name}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={importData}
          className="hidden"
        />
      </div>
    </div>
  );
};

export default PersonalityCompass;