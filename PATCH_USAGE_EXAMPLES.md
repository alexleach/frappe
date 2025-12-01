# PATCH Request Usage Examples

This document provides practical examples of using PATCH requests for partial document updates in Frappe.

## Table of Contents

1. [Basic Field Updates](#basic-field-updates)
2. [Multiple Field Updates](#multiple-field-updates)
3. [Child Table Updates](#child-table-updates)
4. [REST API Examples](#rest-api-examples)
5. [Client-Side JavaScript Examples](#client-side-javascript-examples)
6. [Performance Comparison](#performance-comparison)

## Basic Field Updates

### Update a Single Field

**Python:**
```python
import frappe

# Update just the email field
frappe.client.set_value(
    doctype="Customer",
    name="CUST-001",
    fieldname="email",
    value="updated@example.com"
)
```

**JavaScript:**
```javascript
// Client-side field update
frappe.call({
    method: "frappe.client.set_value",
    args: {
        doctype: "Customer",
        name: "CUST-001",
        fieldname: "email",
        value: "updated@example.com"
    },
    callback: function(r) {
        console.log("Updated:", r.message);
    }
});
```

**REST API (cURL):**
```bash
curl -X PATCH 'https://your-site.com/api/method/frappe.client.set_value' \
  -H 'Authorization: token YOUR_API_KEY:YOUR_API_SECRET' \
  -H 'Content-Type: application/json' \
  -d '{
    "doctype": "Customer",
    "name": "CUST-001",
    "fieldname": "email",
    "value": "updated@example.com"
  }'
```

## Multiple Field Updates

### Update Several Fields at Once

**Python:**
```python
import frappe

# Update multiple fields in one request
frappe.client.set_value(
    doctype="Customer",
    name="CUST-001",
    fieldname={
        "email": "updated@example.com",
        "phone": "+1-555-0123",
        "customer_group": "Commercial"
    }
)
```

**JavaScript:**
```javascript
frappe.call({
    method: "frappe.client.set_value",
    args: {
        doctype: "Customer",
        name: "CUST-001",
        fieldname: {
            email: "updated@example.com",
            phone: "+1-555-0123",
            customer_group: "Commercial"
        }
    },
    callback: function(r) {
        frappe.show_alert({
            message: "Customer updated successfully",
            indicator: "green"
        });
    }
});
```

## Child Table Updates

### Update a Child Table Row

**Python:**
```python
import frappe

# Update a specific child row
frappe.client.set_value(
    doctype="Sales Order Item",  # Child table doctype
    name="SOI-001",              # Child row name
    fieldname={
        "qty": 10,
        "rate": 150.00
    }
)
```

## REST API Examples

### Using fetch/axios in JavaScript

```javascript
// Using fetch API
async function updateCustomer(name, fields) {
    const response = await fetch('/api/method/frappe.client.set_value', {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': frappe.csrf_token
        },
        body: JSON.stringify({
            doctype: 'Customer',
            name: name,
            fieldname: fields
        })
    });
    
    const result = await response.json();
    return result.message;
}

// Usage
updateCustomer('CUST-001', {
    email: 'newemail@example.com',
    phone: '+1-555-0123'
}).then(doc => {
    console.log('Updated:', doc);
});
```

### Using Python requests library

```python
import requests

# API credentials
api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

# PATCH request
response = requests.patch(
    "https://your-site.com/api/method/frappe.client.set_value",
    headers={
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    },
    json={
        "doctype": "Customer",
        "name": "CUST-001",
        "fieldname": {
            "email": "updated@example.com",
            "phone": "+1-555-0123"
        }
    }
)

updated_doc = response.json()["message"]
print(f"Updated customer: {updated_doc['name']}")
```

## Client-Side JavaScript Examples

### Tracking Changed Fields

```javascript
// The client automatically tracks changed fields
let doc = locals["Customer"]["CUST-001"];

// Make some changes
frappe.model.set_value("Customer", "CUST-001", "email", "new@example.com");
frappe.model.set_value("Customer", "CUST-001", "phone", "+1-555-0123");

// Check which fields changed
let changed = frappe.model.get_changed_fields(doc);
console.log("Changed fields:", Array.from(changed)); 
// Output: ["email", "phone"]

// After saving, clear the tracking
frappe.model.clear_changed_fields(doc);
```

### Form Field Updates

```javascript
// In a form script
frappe.ui.form.on('Customer', {
    refresh: function(frm) {
        frm.add_custom_button('Quick Update', function() {
            // Update specific fields without loading the full form
            frappe.call({
                method: "frappe.client.set_value",
                args: {
                    doctype: frm.doctype,
                    name: frm.docname,
                    fieldname: {
                        customer_group: "Retail",
                        territory: "All Territories"
                    }
                },
                callback: function(r) {
                    frm.reload_doc();
                }
            });
        });
    }
});
```

## Performance Comparison

### Traditional POST (Full Document)

```javascript
// Old way - sends entire document (~5KB for a typical customer)
frappe.call({
    method: "frappe.client.save",
    args: {
        doc: {
            doctype: "Customer",
            name: "CUST-001",
            customer_name: "Acme Corp",
            customer_type: "Company",
            customer_group: "Commercial",
            territory: "United States",
            email: "updated@example.com",  // Only this changed
            phone: "+1-555-9999",
            mobile: "+1-555-8888",
            website: "https://acmecorp.com",
            // ... 50 more fields ...
        }
    }
});
```

### PATCH Request (Only Changed Fields)

```javascript
// New way - sends only changed fields (~0.2KB)
frappe.call({
    method: "frappe.client.set_value",
    args: {
        doctype: "Customer",
        name: "CUST-001",
        fieldname: {
            email: "updated@example.com"  // Only send what changed
        }
    }
});
```

**Results:**
- **Network Traffic**: Reduced by ~96% (5KB → 0.2KB)
- **Processing Time**: Faster serialization/deserialization
- **Concurrency**: Better support for simultaneous updates

## Advanced Usage

### Conditional Updates

```python
import frappe

def update_if_changed(doctype, name, new_values):
    """Update only if values actually changed"""
    doc = frappe.get_doc(doctype, name)
    
    changed_values = {}
    for field, new_value in new_values.items():
        if doc.get(field) != new_value:
            changed_values[field] = new_value
    
    if changed_values:
        frappe.client.set_value(doctype, name, changed_values)
        return True
    return False

# Usage
was_updated = update_if_changed("Customer", "CUST-001", {
    "email": "same@example.com",  # Might not change
    "phone": "+1-555-NEW"          # Likely changed
})
```

### Batch Updates

```python
import frappe

def batch_update_customers(updates):
    """Update multiple customers efficiently"""
    for customer_name, fields in updates.items():
        frappe.client.set_value(
            doctype="Customer",
            name=customer_name,
            fieldname=fields
        )
    frappe.db.commit()

# Usage
batch_update_customers({
    "CUST-001": {"customer_group": "VIP"},
    "CUST-002": {"customer_group": "VIP"},
    "CUST-003": {"territory": "Asia"}
})
```

### Error Handling

```javascript
frappe.call({
    method: "frappe.client.set_value",
    args: {
        doctype: "Customer",
        name: "CUST-001",
        fieldname: {
            email: "invalidemail"  // Will trigger validation
        }
    },
    callback: function(r) {
        if (!r.exc) {
            frappe.show_alert("Updated successfully", 5);
        }
    },
    error: function(r) {
        frappe.msgprint({
            title: "Update Failed",
            message: r.message || "An error occurred",
            indicator: "red"
        });
    }
});
```

## Best Practices

1. **Use PATCH for Small Updates**: When updating 1-3 fields, use PATCH
2. **Use POST for New Documents**: For creating new documents, use insert()
3. **Use PUT for Large Updates**: When updating most fields, use full save()
4. **Validate Before Update**: Check field values before making PATCH requests
5. **Handle Errors Gracefully**: Always implement error callbacks
6. **Batch When Possible**: Group multiple updates together
7. **Clear Change Tracking**: Call `clear_changed_fields()` after successful saves

## Common Pitfalls

### Don't Update Standard Fields

```python
# ❌ BAD - Will raise an error
frappe.client.set_value("Customer", "CUST-001", {
    "modified": "2024-01-01",  # Standard field - protected
    "creation": "2024-01-01"   # Standard field - protected
})

# ✅ GOOD - Only update custom/business fields
frappe.client.set_value("Customer", "CUST-001", {
    "email": "new@example.com",
    "customer_group": "VIP"
})
```

### Check Permissions

```python
# Always ensure user has write permission
if frappe.has_permission("Customer", "write", "CUST-001"):
    frappe.client.set_value("Customer", "CUST-001", {
        "email": "new@example.com"
    })
else:
    frappe.throw("Insufficient permissions")
```

## Summary

PATCH requests provide an efficient way to update documents by:
- Reducing network bandwidth usage
- Improving response times
- Enabling better concurrent updates
- Maintaining full backward compatibility

Use PATCH for targeted field updates and traditional POST/PUT for complete document operations.
