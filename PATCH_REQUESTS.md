# PATCH Request Support for Partial Document Updates

## Overview

Frappe now supports HTTP PATCH requests for partial document updates. This feature reduces network traffic by allowing clients to send only the fields that have changed, rather than the entire document.

## Benefits

1. **Reduced Network Traffic**: Only changed fields are transmitted, especially beneficial for documents with many fields
2. **Better Concurrency**: Multiple users can update different fields of the same document simultaneously without conflicts
3. **Improved Performance**: Less data to serialize, transmit, and parse
4. **Backward Compatible**: Existing POST/PUT requests continue to work as before

## How It Works

### Client-Side Field Tracking

The client-side model (`frappe/public/js/frappe/model/model.js`) now automatically tracks which fields have been modified:

```javascript
// When a field value changes, it's tracked in __changed_fields
frappe.model.set_value(doctype, docname, fieldname, value);

// Get the set of changed fields
let changed_fields = frappe.model.get_changed_fields(doc);

// Clear changed fields after save
frappe.model.clear_changed_fields(doc);
```

### Server-Side PATCH Support

Two endpoints now support PATCH requests:

#### 1. `frappe.client.set_value()` - For field-level updates

```python
# PATCH request to update specific fields
frappe.client.set_value("ToDo", "TODO-001", "description", "Updated text")

# Or update multiple fields at once
frappe.client.set_value("ToDo", "TODO-001", {
    "description": "Updated text",
    "priority": "High"
})
```

#### 2. `frappe.client.save()` - For document updates

```python
# PATCH request with partial document
frappe.client.save({
    "doctype": "ToDo",
    "name": "TODO-001",
    "description": "Updated text",
    "priority": "High"
})
```

## Usage Examples

### Python/REST API

```python
import frappe

# Using set_value for partial updates
frappe.client.set_value(
    doctype="Customer",
    name="CUST-001",
    fieldname={
        "email": "newemail@example.com",
        "phone": "+1234567890"
    }
)
```

### JavaScript Client

```javascript
// Track changes automatically
frappe.model.set_value("Customer", "CUST-001", "email", "newemail@example.com");
frappe.model.set_value("Customer", "CUST-001", "phone", "+1234567890");

// The __changed_fields set will contain: ["email", "phone"]

// When saving, only changed fields can be sent (future enhancement)
```

### HTTP REST API

```bash
# PATCH request to update specific fields
curl -X PATCH https://example.com/api/method/frappe.client.set_value \
  -H "Content-Type: application/json" \
  -d '{
    "doctype": "Customer",
    "name": "CUST-001",
    "fieldname": {"email": "newemail@example.com", "phone": "+1234567890"}
  }'
```

## Implementation Details

### Changed Files

1. **frappe/public/js/frappe/model/model.js**
   - Added `__changed_fields` tracking in `set_value()`
   - Added `get_changed_fields()` helper
   - Added `clear_changed_fields()` helper

2. **frappe/client.py**
   - Updated `save()` to accept PATCH method
   - Updated `set_value()` to accept PATCH method

3. **frappe/tests/test_client.py**
   - Added `test_patch_request_for_partial_update()`
   - Added `test_save_with_patch_method()`

## Backward Compatibility

All existing code continues to work without modification:
- POST and PUT requests work as before
- Full document updates are still supported
- No changes required to existing client code

## Future Enhancements

Potential improvements for future versions:

1. **Automatic PATCH Usage**: Modify form save logic to automatically use PATCH when appropriate
2. **Conflict Detection**: Add modified timestamp checking for optimistic locking
3. **Field-Level Permissions**: Validate write permissions for each changed field
4. **Audit Trail**: Enhanced tracking of which fields changed in version history

## Migration Guide

### For Existing Applications

No migration is required. The PATCH support is additive and maintains full backward compatibility.

### For New Developments

To take advantage of PATCH support:

1. Use `frappe.client.set_value()` for field-level updates
2. Specify PATCH as the HTTP method when making REST calls
3. Send only the changed fields in the request payload

## Technical Notes

### HTTP Method Validation

The whitelist decorator validates allowed HTTP methods:

```python
@frappe.whitelist(methods=["POST", "PUT", "PATCH"])
def save(doc):
    # Implementation
```

### Standard Fields Protection

Standard fields (like `creation`, `modified`, `owner`, etc.) cannot be modified via set_value or PATCH requests for data integrity.

## Testing

Run the test suite to verify PATCH functionality:

```bash
# Run client tests
python -m frappe.test_runner --module frappe.tests.test_client

# Specific PATCH tests
python -m frappe.test_runner --test frappe.tests.test_client.TestClient.test_patch_request_for_partial_update
python -m frappe.test_runner --test frappe.tests.test_client.TestClient.test_save_with_patch_method
```

## References

- [HTTP PATCH Method - RFC 5789](https://tools.ietf.org/html/rfc5789)
- [REST API Design Best Practices](https://restfulapi.net/http-methods/)
- [Frappe Framework Documentation](https://frappeframework.com/docs)
