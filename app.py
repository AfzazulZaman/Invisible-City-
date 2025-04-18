from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import json
import os

# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invisible_city.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define Building model
class Building(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    x_position = db.Column(db.Integer)
    y_position = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'description': self.description,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'x_position': self.x_position,
            'y_position': self.y_position
        }


# Create the database if it doesn't exist
with app.app_context():
    db.create_all()

# Building types with associated icons
BUILDING_TYPES = {
    "house": "🏠",
    "apartment": "🏢",
    "library": "📚",
    "fountain": "⛲",
    "park": "🌳",
    "shop": "🏪",
    "museum": "🏛️",
    "cafe": "☕",
    "theater": "🎭",
    "statue": "🗿",
    "garden": "🌷",
    "office": "🏢",
    "school": "🏫",
    "hospital": "🏥",
    "hotel": "🏨",
    "restaurant": "🍽️",
    "factory": "🏭",
    "weird_sculpture": "🗿"
}

# Main index page template
index_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invisible City</title>
    <style>
        /* City styling */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f8ff;
            color: #333;
            margin: 0;
            padding: 0;
            transition: background-color 0.5s;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            padding: 20px 0;
            background-color: #5f9ea0;
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        header h1 {
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }

        header p {
            font-size: 1.2em;
            margin: 10px 0 0;
            font-style: italic;
        }

        .city-view {
            position: relative;
            background-color: #e6f7ff;
            border-radius: 10px;
            padding: 20px;
            min-height: 600px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            overflow: hidden;
        }

        .city-grid {
            position: relative;
            width: 100%;
            height: 600px;
            background-image: linear-gradient(#e6f7ff 1px, transparent 1px), 
                              linear-gradient(90deg, #e6f7ff 1px, transparent 1px);
            background-size: 50px 50px;
            background-color: #f0f8ff;
            border: 2px solid #5f9ea0;
            border-radius: 8px;
        }

        .building {
            position: absolute;
            width: 60px;
            height: 60px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 10px;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            overflow: hidden;
            z-index: 1;
        }

        .building:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            z-index: 2;
        }

        .building-icon {
            font-size: 24px;
            display: block;
            text-align: center;
            margin-bottom: 5px;
        }

        .building-type {
            font-weight: bold;
            text-align: center;
            font-size: 0.8em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .building-popup {
            position: absolute;
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            width: 250px;
            z-index: 10;
            display: none;
            animation: fadeIn 0.3s;
        }

        .building-popup h3 {
            margin-top: 0;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
            color: #5f9ea0;
        }

        .building-popup p {
            margin: 5px 0;
            line-height: 1.4;
        }

        .building-popup .timestamp {
            font-size: 0.8em;
            color: #777;
            font-style: italic;
            margin-top: 10px;
        }

        .form-container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .form-row {
            display: flex;
            margin-bottom: 15px;
        }

        .form-group {
            flex: 1;
            margin-right: 10px;
        }

        .form-group:last-child {
            margin-right: 0;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #5f9ea0;
        }

        .form-control {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1em;
        }

        .btn {
            background-color: #5f9ea0;
            color: white;
            border: none;
            padding: 12px 20px;
            font-size: 1em;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        .btn:hover {
            background-color: #4f8e90;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes buildingAppear {
            0% { transform: scale(0); opacity: 0; }
            70% { transform: scale(1.1); }
            100% { transform: scale(1); opacity: 1; }
        }

        .building-new {
            animation: buildingAppear 0.5s;
        }

        footer {
            text-align: center;
            padding: 20px 0;
            color: #777;
            font-size: 0.9em;
        }

        .stats {
            display: flex;
            justify-content: space-around;
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .stat-box {
            text-align: center;
        }

        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #5f9ea0;
        }

        .stat-label {
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Invisible City</h1>
            <p>A digital city that grows with every visitor</p>
        </header>

        <div class="stats">
            <div class="stat-box">
                <div class="stat-value" id="total-buildings">{{ buildings|length }}</div>
                <div class="stat-label">Buildings</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" id="last-built">
                    {% if buildings %}
                        {{ (buildings|sort(attribute='timestamp', reverse=True))[0].timestamp.strftime('%H:%M:%S') }}
                    {% else %}
                        --:--:--
                    {% endif %}
                </div>
                <div class="stat-label">Last Addition</div>
            </div>
        </div>

        <div class="city-view">
            <div class="city-grid" id="city-grid">
                {% for building in buildings %}
                <div class="building" id="building-{{ building.id }}" data-id="{{ building.id }}" 
                     style="left: {{ building.x_position }}px; top: {{ building.y_position }}px;">
                    <span class="building-icon">{{ building_icons[building.type] }}</span>
                    <div class="building-type">{{ building.type.replace('_', ' ').title() }}</div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="form-container">
            <h2>Add to the City</h2>
            <form id="add-building-form">
                <div class="form-row">
                    <div class="form-group">
                        <label for="building-type">Building Type</label>
                        <select id="building-type" name="type" class="form-control" required>
                            {% for type in building_types %}
                            <option value="{{ type }}">{{ type.replace('_', ' ').title() }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="building-description">Description</label>
                        <input type="text" id="building-description" name="description" class="form-control" 
                               placeholder="Describe this building...">
                    </div>
                </div>
                <button type="submit" class="btn">Add Building</button>
            </form>
        </div>

        <footer>
            <p>&copy; 2025 Invisible City - A growing digital metropolis</p>
        </footer>
    </div>

    <div class="building-popup" id="building-popup">
        <h3 id="popup-title">Building Information</h3>
        <p id="popup-description">Description goes here</p>
        <p class="timestamp" id="popup-timestamp">Added on: timestamp</p>
    </div>

    <script>
        // Initialize variables
        const cityGrid = document.getElementById('city-grid');
        const addBuildingForm = document.getElementById('add-building-form');
        const buildingPopup = document.getElementById('building-popup');
        const totalBuildingsEl = document.getElementById('total-buildings');
        const lastBuiltEl = document.getElementById('last-built');

        // Get grid dimensions
        const gridWidth = cityGrid.offsetWidth;
        const gridHeight = cityGrid.offsetHeight;

        // Function to handle building clicks and show popup
        function setupBuildingClicks() {
            document.querySelectorAll('.building').forEach(building => {
                building.addEventListener('click', function(e) {
                    const buildingId = this.getAttribute('data-id');

                    // Get building data from the server
                    fetch(`/api/building/${buildingId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Populate popup with building info
                        document.getElementById('popup-title').textContent = 
                            data.type.replace('_', ' ').charAt(0).toUpperCase() + data.type.replace('_', ' ').slice(1);
                        document.getElementById('popup-description').textContent = data.description || 'No description available';
                        document.getElementById('popup-timestamp').textContent = `Added on: ${data.timestamp}`;

                        // Position popup near the clicked building
                        const buildingRect = this.getBoundingClientRect();
                        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

                        buildingPopup.style.left = `${buildingRect.left + buildingRect.width / 2 - 125}px`;
                        buildingPopup.style.top = `${buildingRect.top + buildingRect.height + scrollTop + 10}px`;
                        buildingPopup.style.display = 'block';

                        // Close popup when clicking elsewhere
                        document.addEventListener('click', closePopup);
                    });

                    e.stopPropagation();
                });
            });
        }

        // Function to close the popup
        function closePopup(e) {
            if (!buildingPopup.contains(e.target) && !e.target.classList.contains('building')) {
                buildingPopup.style.display = 'none';
                document.removeEventListener('click', closePopup);
            }
        }

        // Handle form submission
        addBuildingForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Get form data
            const type = document.getElementById('building-type').value;
            const description = document.getElementById('building-description').value;

            // Generate random position
            const xPos = Math.floor(Math.random() * (gridWidth - 100)) + 20;
            const yPos = Math.floor(Math.random() * (gridHeight - 100)) + 20;

            // Send data to server
            fetch('/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: type,
                    description: description,
                    x_position: xPos,
                    y_position: yPos
                })
            })
            .then(response => response.json())
            .then(data => {
                // Add the new building to the city
                const newBuilding = document.createElement('div');
                newBuilding.className = 'building building-new';
                newBuilding.id = `building-${data.id}`;
                newBuilding.setAttribute('data-id', data.id);
                newBuilding.style.left = `${data.x_position}px`;
                newBuilding.style.top = `${data.y_position}px`;

                // Add building icon and type
                const iconSpan = document.createElement('span');
                iconSpan.className = 'building-icon';
                iconSpan.textContent = data.icon;

                const typeDiv = document.createElement('div');
                typeDiv.className = 'building-type';
                typeDiv.textContent = data.type.replace('_', ' ').charAt(0).toUpperCase() + data.type.replace('_', ' ').slice(1);

                newBuilding.appendChild(iconSpan);
                newBuilding.appendChild(typeDiv);

                cityGrid.appendChild(newBuilding);

                // Update stats
                totalBuildingsEl.textContent = parseInt(totalBuildingsEl.textContent) + 1;
                lastBuiltEl.textContent = new Date().toTimeString().slice(0, 8);

                // Reset form
                addBuildingForm.reset();

                // Setup click event for the new building
                setupBuildingClicks();
            });
        });

        // Initialize the building clicks
        setupBuildingClicks();
    </script>
</body>
</html>
'''


# Routes
@app.route('/')
def index():
    # Get all buildings from the database
    buildings = Building.query.all()

    return render_template_string(
        index_template,
        buildings=buildings,
        building_types=list(BUILDING_TYPES.keys()),
        building_icons=BUILDING_TYPES
    )


@app.route('/add', methods=['POST'])
def add_building():
    # Get JSON data from the request
    data = request.get_json()

    # Create a new building
    new_building = Building(
        type=data['type'],
        description=data['description'],
        x_position=data['x_position'],
        y_position=data['y_position']
    )

    # Add to the database
    db.session.add(new_building)
    db.session.commit()

    # Return the new building data with its icon
    return jsonify({
        'id': new_building.id,
        'type': new_building.type,
        'description': new_building.description,
        'timestamp': new_building.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'x_position': new_building.x_position,
        'y_position': new_building.y_position,
        'icon': BUILDING_TYPES.get(new_building.type, '🏢')
    })


@app.route('/api/buildings')
def get_buildings():
    # Get all buildings and return as JSON
    buildings = Building.query.all()
    return jsonify([building.to_dict() for building in buildings])


@app.route('/api/building/<int:building_id>')
def get_building(building_id):
    # Get a specific building by ID
    building = Building.query.get_or_404(building_id)
    building_data = building.to_dict()
    building_data['icon'] = BUILDING_TYPES.get(building.type, '🏢')
    return jsonify(building_data)


# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=5000)