"""Flask web application for warehouse management."""
from flask import Flask, render_template, request, redirect, url_for

from varasto import Varasto

app = Flask(__name__)


class WarehouseStore:
    """Manages warehouse storage and ID generation."""

    def __init__(self):
        self.warehouses = {}
        self._next_id = 1

    def get_next_id(self):
        """Get next available ID for a warehouse."""
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def get(self, warehouse_id):
        """Get a warehouse by ID."""
        return self.warehouses.get(warehouse_id)

    def add(self, warehouse):
        """Add a warehouse."""
        self.warehouses[warehouse['id']] = warehouse

    def delete(self, warehouse_id):
        """Delete a warehouse by ID."""
        if warehouse_id in self.warehouses:
            del self.warehouses[warehouse_id]

    def all(self):
        """Get all warehouses."""
        return self.warehouses


store = WarehouseStore()


@app.route('/')
def index():
    """Display all warehouses."""
    return render_template('index.html', warehouses=store.all())


@app.route('/warehouse/create', methods=['GET', 'POST'])
def create_warehouse():
    """Create a new warehouse."""
    if request.method == 'POST':
        name = request.form.get('name', 'Unnamed')
        tilavuus = float(request.form.get('tilavuus', 100))
        alku_saldo = float(request.form.get('alku_saldo', 0))

        warehouse_id = store.get_next_id()
        store.add({
            'id': warehouse_id,
            'name': name,
            'varasto': Varasto(tilavuus, alku_saldo)
        })
        return redirect(url_for('index'))

    return render_template('create_warehouse.html')


@app.route('/warehouse/<int:warehouse_id>')
def view_warehouse(warehouse_id):
    """View a specific warehouse."""
    warehouse = store.get(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))
    return render_template('view_warehouse.html', warehouse=warehouse)


@app.route('/warehouse/<int:warehouse_id>/edit', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    """Edit a warehouse's name and capacity."""
    warehouse = store.get(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', warehouse['name'])
        default_tilavuus = warehouse['varasto'].tilavuus
        new_tilavuus = float(request.form.get('tilavuus', default_tilavuus))

        warehouse['name'] = name
        # Update capacity if changed (reset saldo if capacity is smaller)
        old_saldo = warehouse['varasto'].saldo
        warehouse['varasto'] = Varasto(new_tilavuus, old_saldo)

        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    return render_template('edit_warehouse.html', warehouse=warehouse)


@app.route('/warehouse/<int:warehouse_id>/add', methods=['POST'])
def add_to_warehouse(warehouse_id):
    """Add items to a warehouse."""
    warehouse = store.get(warehouse_id)
    if warehouse:
        amount = float(request.form.get('amount', 0))
        warehouse['varasto'].lisaa_varastoon(amount)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/remove', methods=['POST'])
def remove_from_warehouse(warehouse_id):
    """Remove items from a warehouse."""
    warehouse = store.get(warehouse_id)
    if warehouse:
        amount = float(request.form.get('amount', 0))
        warehouse['varasto'].ota_varastosta(amount)
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/delete', methods=['POST'])
def delete_warehouse(warehouse_id):
    """Delete a warehouse."""
    store.delete(warehouse_id)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
