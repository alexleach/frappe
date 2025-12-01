# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.tests import IntegrationTestCase


class TestLazyLoading(IntegrationTestCase):
	def setUp(self):
		# Create a test document with child table
		self.test_doc = frappe.get_doc({
			"doctype": "Note",
			"title": f"Test Note for Lazy Loading {frappe.generate_hash()}",
			"content": "Test content",
			"seen_by": [
				{"user": "Administrator"},
				{"user": "Guest"}
			]
		}).insert()

	def tearDown(self):
		if hasattr(self, 'test_doc') and self.test_doc:
			frappe.delete_doc("Note", self.test_doc.name, force=True)

	def test_getdoc_with_child_limit(self):
		"""Test lazy loading of child table rows with limit"""
		from frappe.desk.form.load import getdoc
		
		# Call getdoc with child_limit
		frappe.set_user("Administrator")
		frappe.local.response = frappe._dict({"docs": []})
		
		getdoc(self.test_doc.doctype, self.test_doc.name, child_limit=1)
		
		doc = frappe.response.docs[0]
		
		# Check that only 1 child row was loaded
		self.assertEqual(len(doc.seen_by), 1)
		
		# Check that pagination metadata exists
		self.assertIn('child_table_counts', doc.__onload)
		self.assertIn('seen_by', doc.__onload.child_table_counts)
		
		# Verify pagination metadata
		metadata = doc.__onload.child_table_counts['seen_by']
		self.assertEqual(metadata['total'], 2)
		self.assertEqual(metadata['loaded'], 1)
		self.assertTrue(metadata['has_more'])

	def test_getdoc_with_lazy_docinfo(self):
		"""Test minimal docinfo loading"""
		from frappe.desk.form.load import getdoc
		
		frappe.set_user("Administrator")
		frappe.local.response = frappe._dict({"docs": []})
		frappe.local.response["docinfo"] = None
		
		getdoc(self.test_doc.doctype, self.test_doc.name, lazy_docinfo=True)
		
		docinfo = frappe.response.docinfo
		
		# Check that only minimal docinfo is loaded
		self.assertIn('permissions', docinfo)
		self.assertIn('is_document_followed', docinfo)
		
		# Check that heavy data is NOT loaded
		self.assertNotIn('communications', docinfo)
		self.assertNotIn('attachments', docinfo)
		self.assertNotIn('versions', docinfo)

	def test_get_child_table_rows(self):
		"""Test pagination endpoint for child table rows"""
		from frappe.desk.form.load import get_child_table_rows
		
		frappe.set_user("Administrator")
		
		result = get_child_table_rows(
			self.test_doc.doctype,
			self.test_doc.name,
			"seen_by",
			limit=1,
			offset=0
		)
		
		self.assertEqual(len(result['rows']), 1)
		self.assertEqual(result['total'], 2)
		self.assertTrue(result['has_more'])
		
		# Test second page
		result2 = get_child_table_rows(
			self.test_doc.doctype,
			self.test_doc.name,
			"seen_by",
			limit=1,
			offset=1
		)
		
		self.assertEqual(len(result2['rows']), 1)
		self.assertFalse(result2['has_more'])

	def test_get_docinfo_comments(self):
		"""Test lazy-loading of comments"""
		from frappe.desk.form.load import get_docinfo_comments
		
		# Add a comment
		frappe.get_doc({
			"doctype": "Comment",
			"comment_type": "Comment",
			"reference_doctype": self.test_doc.doctype,
			"reference_name": self.test_doc.name,
			"content": "Test comment"
		}).insert()
		
		frappe.set_user("Administrator")
		
		result = get_docinfo_comments(self.test_doc.doctype, self.test_doc.name)
		
		self.assertIn('comments', result)
		self.assertGreater(len(result['comments']), 0)

	def test_get_docinfo_timeline(self):
		"""Test lazy-loading of timeline data"""
		from frappe.desk.form.load import get_docinfo_timeline
		
		frappe.set_user("Administrator")
		
		result = get_docinfo_timeline(self.test_doc.doctype, self.test_doc.name)
		
		# Check that timeline data is present
		self.assertIn('communications', result)
		self.assertIn('milestones', result)
		self.assertIn('views', result)
		self.assertIn('user_info', result)
