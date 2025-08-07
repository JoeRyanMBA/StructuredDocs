# Collection ID (Form Number) Field Implementation

## Summary

Successfully implemented a required "Collection ID (Form Number)" field for Collections in the StructuredDocs application. This alphanumeric field serves as a unique identifier for each collection/document.

## Changes Made

### 1. Database Changes
- **Added `form_number` column** to the `collections` table
  - Type: `VARCHAR(100)`
  - Constraints: `NOT NULL`, `UNIQUE`
- **Migration file**: `20250806_add_form_number_to_collections.py`
  - Safely adds the column with temporary values for existing collections
  - Enforces uniqueness constraint

### 2. Backend Changes

#### Models (`backend/models.py`)
```python
class Collection(db.Model):
    # ... existing fields ...
    form_number = db.Column(db.String(100), nullable=False, unique=True)
    
    def to_dict(self, include_children=True, include_topics=True):
        data = {
            'id': self.id,
            'name': self.name,
            'form_number': self.form_number,  # NEW FIELD
            # ... other fields ...
        }
```

#### API Routes (`backend/routes/collections.py`)
```python
@collections_bp.route('', methods=['POST'])
def create_collection():
    """
    Create a new collection.
    Expects JSON payload: { 
        "name": str, 
        "form_number": str,      # NEW REQUIRED FIELD
        "parentId": int (optional), 
        "position": int (optional),
        "projectId": int (optional)
    }
    """
    # Validates form_number is provided
    # Checks for uniqueness
    # Returns appropriate error messages
```

### 3. Frontend Changes

#### Collections Dashboard (`frontend/src/views/CollectionsDashboard.vue`)
- Added form field for Collection ID (Form Number)
- Added validation pattern: `^[A-Za-z0-9\-_]+$`
- Added help text explaining the field purpose
- Updated form submission to include `form_number`

#### Document Builder (`frontend/src/views/DocumentBuilder.vue`)
- Added form field for Collection ID (Form Number)
- Added validation and help text
- Updated data model and form submission

#### Simple Collections View (`frontend/src/views/Collections.vue`)
- Updated simple form to include form_number field
- Added inline form layout with help text
- Added error handling for duplicate form numbers

## Usage Examples

### Creating a Collection via API

```bash
# Successful creation
curl -X POST http://localhost:5050/api/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Employee Handbook", 
    "form_number": "HR-001",
    "projectId": 1
  }'

# Duplicate form_number (will fail)
curl -X POST http://localhost:5050/api/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Another Document", 
    "form_number": "HR-001"
  }'
# Returns: {"error": "Collection ID \"HR-001\" already exists"}
```

### Frontend Form Validation

The frontend forms now include:
- **Required field validation**: User cannot submit without providing a form number
- **Pattern validation**: Only alphanumeric characters, hyphens, and underscores allowed
- **Helpful placeholder text**: `"e.g., FORM-001, DOC-ABC-123"`
- **User guidance**: Help text explaining the purpose and format

### Example Form Numbers

Good examples:
- `FORM-001`
- `DOC-ABC-123`
- `HR_HANDBOOK_V2`
- `POLICY-001`
- `PROC-SAFETY-001`

Invalid examples:
- `FORM 001` (spaces not allowed)
- `DOC@123` (special characters not allowed)
- `FORM/001` (slashes not allowed)

## Database Migration

The migration was successfully applied:
```bash
cd backend
python -m flask db upgrade
```

Migration ID: `20250806_add_form_number`

## Testing

All functionality tested and verified:
- ✅ Collection creation with form_number
- ✅ Uniqueness constraint enforcement
- ✅ API returns form_number in responses
- ✅ Frontend forms include validation
- ✅ Error handling for duplicates

## Backward Compatibility

- Existing collections were given temporary form numbers during migration
- All API responses now include the `form_number` field
- Frontend displays will need to be updated to show form numbers where appropriate

## Next Steps

Consider implementing:
1. **Form number format validation** based on organization standards
2. **Auto-generation** of form numbers with configurable prefixes
3. **Search/filter** by form number in collection lists
4. **Display form number** prominently in collection cards and lists
5. **Form number history** or versioning for document revisions

## Files Modified

- `backend/models.py` - Added form_number field to Collection model
- `backend/routes/collections.py` - Updated create_collection API
- `backend/migrations/versions/20250806_add_form_number_to_collections.py` - New migration
- `frontend/src/views/CollectionsDashboard.vue` - Added form field and validation
- `frontend/src/views/DocumentBuilder.vue` - Added form field and validation  
- `frontend/src/views/Collections.vue` - Updated simple collection form

The Collection ID (Form Number) field is now fully implemented and ready for use!
