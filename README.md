# Personality Compass

If you know, you know.

## ✨ **Core Features**

### **Interactive Grid System**
- **Drag & Drop**: Drag them to place the people of interest where you want them to be
- **Real-time Updates**: Live position updates with visual feedback
- **Quadrant Detection**: Automatic categorisation into personality quadrants
- **Constraint Handling**: Positions automatically bounded to -100 to +100 range

### **Comprehensive Data Management**
- **Auto-save**: People's data in hidden JSON folder
- **Cross-platform Folder Hiding**: Hidden data storage on Windows, macOS, and Linux
- **Export/Import Ready**: Structured JSON format for data portability
- **Edit History Tracking**: Complete audit trail of all user actions

### **Advanced Coordinate Editing**
- **Manual Input**: Precise coordinate entry via input fields
- **Auto-population**: Coordinate fields update when selecting people
- **Multiple Edit Methods**: 
 - Select person → edit coordinates → update
 - Double-click person → instant edit mode
 - Type coordinates → press Enter to apply
- **Input Validation**: Error handling for invalid coordinate values
- **Real-time Sync**: Coordinates sync between manual input and drag operations

## **User Interface**

### **Main Components**
- **Person Management Panel**: Add/remove people with name input
- **Interactive Grid**: Matplotlib-powered coordinate system with quadrant labels
- **People List**: Scrollable list showing names, coordinates, and quadrants
- **Coordinate Editor**: Manual X/Y input fields with update functionality
- **Instructions Panel**: Comprehensive help and keyboard shortcuts

### **Visual Design**
- **Quadrant Labels**: Color-coded corner labels (Gnatty/Not × NPC/Non-NPC)
- **Grid System**: Professional grid lines with center axis emphasis
- **Person Markers**: Red dots with name labels that follow during movement
- **Responsive Layout**: Scalable interface that adapts to window resizing

## ⌨️ **Keyboard Shortcuts & Controls**

### **Keyboard Shortcuts**
- **Enter**: Add person after typing name
- **Delete/Backspace**: Remove selected person from list
- **Escape**: Cancel current drag operation
- **Enter** (in coordinate fields): Apply coordinate changes

### **Mouse Controls**
- **Left-click + Drag**: Move person on grid
- **Right-click**: Remove person from grid
- **Double-click** (on list item): Load coordinates for editing
- **Single-click** (on list item): Select person and show coordinates

## 🗂️ **Data Structure & Persistence**

(All names)

### **JSON Data Format**
```json
{
 "metadata": {
   "last_updated": "2025-07-30 15:22:45.123",
   "total_people": 3,
   "version": "2.1",
   "total_edits": 25,
   "session_started": "2025-07-30 15:10:30"
 },
 "edit_history": [
   {
     "timestamp": "2025-07-30 15:12:15.789",
     "action": "person_added",
     "details": {
       "name": "John Cena",
       "position": {"x": 0, "y": 0},
       "quadrant": "Gnatty, NPC"
     }
   },
   {
     "timestamp": "2025-07-30 15:15:45.234",
     "action": "coordinates_edited",
     "details": {
       "name": "John Cena",
       "old_position": {"x": 0, "y": 0},
       "new_position": {"x": 45.2, "y": -23.8},
       "old_quadrant": "Gnatty, NPC",
       "new_quadrant": "Gnatty, Non-NPC",
       "method": "manual_input"
     }
   }
 ],
 "people": {
   "John Cena": {
     "x": 45.2,
     "y": -23.8,
     "quadrant": "Gnatty, Non-NPC",
     "date_added": "2025-07-30 15:12:15",
     "last_moved": "2025-07-30 15:15:45.234"
   }
 }
}