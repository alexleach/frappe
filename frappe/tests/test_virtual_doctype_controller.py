import frappe
from frappe.model.document import Document
from frappe.utils import generate_hash

class TestVirtualController(Document):
    data_store = []

    @staticmethod
    def clear_data():
        TestVirtualController.data_store = []

    # Static methods for VirtualDoctype protocol
    @staticmethod
    def get_list(doctype, parent_doc=None, filters=None, fields=None, limit_start=0, limit_page_length=20, order_by=None):
        data = TestVirtualController.data_store

        if parent_doc:
            data = [d for d in data if d.get('parent') == parent_doc.name]

        if filters:
            for f_key, f_val in filters.items():
                if isinstance(f_val, (list, tuple)) and f_val[0] == 'in':
                    data = [d for d in data if d.get(f_key) in f_val[1]]
                else:
                    data = [d for d in data if d.get(f_key) == f_val]

        # Sorting (simplified: assumes order_by is a field name, asc)
        if order_by:
            # Assuming order_by is in the format "field_name asc" or "field_name desc"
            # For simplicity, this example only handles "field_name" (ascending)
            # and ignores asc/desc. A more robust solution would parse this.
            sort_key = order_by.split(' ')[0]
            data = sorted(data, key=lambda x: x.get(sort_key, 0))


        # Pagination
        start = int(limit_start)
        length = int(limit_page_length)
        data = data[start : start + length]

        # Field selection
        if fields:
            # Ensure 'name' is always included if not explicitly asked for, as it's often expected
            if 'name' not in fields and any('name' in d for d in data):
                 # Make a copy to avoid modifying the input list
                _fields = fields[:]
                if isinstance(_fields, list) and 'name' not in _fields :
                    _fields.append('name')
            else:
                _fields = fields

            result = []
            for doc in data:
                filtered_doc = {}
                for field in _fields:
                    if field in doc:
                        filtered_doc[field] = doc[field]
                result.append(filtered_doc)
            return result
        else:
            # Return all fields if no specific fields are requested
            return data

    @staticmethod
    def get_count(doctype, parent_doc=None, filters=None):
        data = TestVirtualController.data_store

        if parent_doc:
            data = [d for d in data if d.get('parent') == parent_doc.name]

        if filters:
            for f_key, f_val in filters.items():
                if isinstance(f_val, (list, tuple)) and f_val[0] == 'in':
                    data = [d for d in data if d.get(f_key) in f_val[1]]
                else:
                    data = [d for d in data if d.get(f_key) == f_val]

        return len(data)

    @staticmethod
    def get_stats(doctype, parent_doc=None, filters=None):
        # Return a simple predefined dictionary
        return {}

    # Instance methods for VirtualDoctype protocol
    def db_insert(self, *args, **kwargs):
        if not self.name:
            self.name = generate_hash(length=10) # frappe.generate_hash() is not available here

        # Avoid circular references if _doc_before_save is present
        doc_dict = self.as_dict()
        if '_doc_before_save' in doc_dict:
            del doc_dict['_doc_before_save']

        TestVirtualController.data_store.append(doc_dict)
        return self

    def load_from_db(self):
        if not self.name:
            raise frappe.IncompleteTableError("name") # Or some other appropriate error

        record_data = None
        for record in TestVirtualController.data_store:
            if record.get('name') == self.name:
                record_data = record
                break

        if record_data:
            self.update(record_data)
            # self.set_new_name(self.name) # Not typically needed here as name is already set
            return self # Ensure the method returns self as per some Document method expectations
        else:
            raise frappe.DoesNotExistError(f"{self.doctype} {self.name} not found")


    def db_update(self, *args, **kwargs):
        if not self.name:
            # Or handle as an error, but for tests, ensuring a name might be okay.
            self.name = generate_hash(length=10)

        record_exists = False
        for i, record in enumerate(TestVirtualController.data_store):
            if record.get('name') == self.name:
                # Avoid circular references if _doc_before_save is present
                doc_dict = self.as_dict()
                if '_doc_before_save' in doc_dict:
                    del doc_dict['_doc_before_save']
                TestVirtualController.data_store[i] = doc_dict
                record_exists = True
                break

        if not record_exists:
            # If record not found, effectively do an insert
            self.db_insert(*args, **kwargs) # This will handle adding it to data_store

        return self


    def delete(self, *args, **kwargs):
        if not self.name:
            # Nothing to delete if name is not set
            return

        original_length = len(TestVirtualController.data_store)
        TestVirtualController.data_store = [
            record for record in TestVirtualController.data_store
            if record.get('name') != self.name
        ]

        if len(TestVirtualController.data_store) == original_length:
            # Optional: could raise an error if the document was not found,
            # but for tests, it might be acceptable to do nothing.
            # frappe.log_error(f"Record {self.name} not found for deletion.", self.doctype)
            pass # Or raise frappe.DoesNotExistError(f"{self.doctype} {self.name} not found for deletion")

        # After deletion, the instance in memory still exists but is "deleted"
        # Frappe's standard Document.delete() also sets self.flags.deleted = True
        self.flags.deleted = True
        return self
