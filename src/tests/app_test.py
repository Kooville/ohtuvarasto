"""Tests for the Flask web application."""
import unittest
from app import app, store, safe_float


class TestFlaskApp(unittest.TestCase):
    """Test cases for the Flask warehouse app."""

    def setUp(self):
        """Set up test fixtures."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        # Clear the store before each test
        store.warehouses.clear()
        store._next_id = 1  # pylint: disable=protected-access

    def test_index_empty(self):
        """Test index page with no warehouses."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No warehouses yet', response.data)

    def test_create_warehouse_get(self):
        """Test GET request for create warehouse page."""
        response = self.client.get('/warehouse/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Warehouse', response.data)

    def test_create_warehouse_post(self):
        """Test POST request to create a warehouse."""
        response = self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Warehouse', response.data)
        self.assertEqual(len(store.warehouses), 1)

    def test_view_warehouse(self):
        """Test viewing a specific warehouse."""
        # Create a warehouse first
        self.client.post('/warehouse/create', data={
            'name': 'View Test',
            'tilavuus': '200',
            'alku_saldo': '75'
        })

        response = self.client.get('/warehouse/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'View Test', response.data)
        self.assertIn(b'200', response.data)
        self.assertIn(b'75', response.data)

    def test_view_nonexistent_warehouse(self):
        """Test viewing a warehouse that doesn't exist."""
        response = self.client.get('/warehouse/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Should redirect to index
        self.assertIn(b'No warehouses yet', response.data)

    def test_edit_warehouse_get(self):
        """Test GET request for edit warehouse page."""
        self.client.post('/warehouse/create', data={
            'name': 'Edit Test',
            'tilavuus': '150',
            'alku_saldo': '0'
        })

        response = self.client.get('/warehouse/1/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Warehouse', response.data)
        self.assertIn(b'Edit Test', response.data)

    def test_edit_warehouse_post(self):
        """Test POST request to edit a warehouse."""
        self.client.post('/warehouse/create', data={
            'name': 'Original Name',
            'tilavuus': '100',
            'alku_saldo': '50'
        })

        response = self.client.post('/warehouse/1/edit', data={
            'name': 'Updated Name',
            'tilavuus': '200'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Updated Name', response.data)
        warehouse = store.get(1)
        self.assertEqual(warehouse['name'], 'Updated Name')
        self.assertEqual(warehouse['varasto'].tilavuus, 200)

    def test_add_to_warehouse(self):
        """Test adding items to a warehouse."""
        self.client.post('/warehouse/create', data={
            'name': 'Add Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })

        response = self.client.post('/warehouse/1/add', data={
            'amount': '30'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        warehouse = store.get(1)
        self.assertEqual(warehouse['varasto'].saldo, 30)

    def test_remove_from_warehouse(self):
        """Test removing items from a warehouse."""
        self.client.post('/warehouse/create', data={
            'name': 'Remove Test',
            'tilavuus': '100',
            'alku_saldo': '50'
        })

        response = self.client.post('/warehouse/1/remove', data={
            'amount': '20'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        warehouse = store.get(1)
        self.assertEqual(warehouse['varasto'].saldo, 30)

    def test_delete_warehouse(self):
        """Test deleting a warehouse."""
        self.client.post('/warehouse/create', data={
            'name': 'Delete Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.assertEqual(len(store.warehouses), 1)

        response = self.client.post('/warehouse/1/delete', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(store.warehouses), 0)

    def test_multiple_warehouses(self):
        """Test creating and viewing multiple warehouses."""
        self.client.post('/warehouse/create', data={
            'name': 'Warehouse A',
            'tilavuus': '100',
            'alku_saldo': '25'
        })
        self.client.post('/warehouse/create', data={
            'name': 'Warehouse B',
            'tilavuus': '200',
            'alku_saldo': '75'
        })

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse A', response.data)
        self.assertIn(b'Warehouse B', response.data)
        self.assertEqual(len(store.warehouses), 2)

    def test_add_to_nonexistent_warehouse(self):
        """Test adding to a warehouse that doesn't exist."""
        response = self.client.post('/warehouse/999/add', data={
            'amount': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_remove_from_nonexistent_warehouse(self):
        """Test removing from a warehouse that doesn't exist."""
        response = self.client.post('/warehouse/999/remove', data={
            'amount': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_edit_nonexistent_warehouse(self):
        """Test editing a warehouse that doesn't exist."""
        response = self.client.get('/warehouse/999/edit', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No warehouses yet', response.data)


class TestWarehouseStore(unittest.TestCase):
    """Test cases for the WarehouseStore class."""

    def setUp(self):
        """Set up test fixtures."""
        store.warehouses.clear()
        store._next_id = 1  # pylint: disable=protected-access

    def test_get_next_id(self):
        """Test ID generation."""
        self.assertEqual(store.get_next_id(), 1)
        self.assertEqual(store.get_next_id(), 2)
        self.assertEqual(store.get_next_id(), 3)

    def test_add_and_get(self):
        """Test adding and getting a warehouse."""
        warehouse = {'id': 1, 'name': 'Test'}
        store.add(warehouse)
        self.assertEqual(store.get(1), warehouse)

    def test_delete(self):
        """Test deleting a warehouse."""
        warehouse = {'id': 1, 'name': 'Test'}
        store.add(warehouse)
        store.delete(1)
        self.assertIsNone(store.get(1))

    def test_delete_nonexistent(self):
        """Test deleting a warehouse that doesn't exist."""
        store.delete(999)  # Should not raise an error

    def test_all(self):
        """Test getting all warehouses."""
        store.add({'id': 1, 'name': 'A'})
        store.add({'id': 2, 'name': 'B'})
        all_warehouses = store.all()
        self.assertEqual(len(all_warehouses), 2)


class TestSafeFloat(unittest.TestCase):
    """Test cases for the safe_float helper function."""

    def test_valid_float(self):
        """Test with valid float string."""
        self.assertEqual(safe_float('10.5'), 10.5)

    def test_valid_integer(self):
        """Test with valid integer string."""
        self.assertEqual(safe_float('42'), 42.0)

    def test_invalid_string(self):
        """Test with invalid string returns default."""
        self.assertEqual(safe_float('invalid'), 0.0)

    def test_none_value(self):
        """Test with None value returns default."""
        self.assertEqual(safe_float(None), 0.0)

    def test_custom_default(self):
        """Test with custom default value."""
        self.assertEqual(safe_float('invalid', 100.0), 100.0)

    def test_empty_string(self):
        """Test with empty string returns default."""
        self.assertEqual(safe_float(''), 0.0)
