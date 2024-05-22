# Media Dashboard 🎧📊

Welcome to the Media Dashboard repository by @harperreed! 🙌 This project aims to provide a sleek and informative dashboard for monitoring and controlling your media player using Home Assistant. 🎮🏠

## Features ✨

- Real-time display of currently playing media 🎵
- Artist and title information 🎤🎼
- Progress bar and time indicators ⏳
- Volume control 🔊
- Cover art display 🖼️

## Getting Started 🚀

To get started with the Media Dashboard, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/harperreed/media-dashboard.git
   ```

2. Navigate to the project directory:
   ```
   cd media-dashboard
   ```

3. Update the environment variables in the `docker-compose.yaml` file:
   - Set `BASE_URL` to your Home Assistant URL (e.g., `http://homeassistant.local:8123`)
   - Set `API_TOKEN` to your Home Assistant long-lived access token
   - Set `ENTITY_ID` to the entity ID of your media player in Home Assistant

4. Build and run the Docker containers:
   ```
   docker-compose up --build
   ```

5. Access the Media Dashboard in your web browser at `http://localhost:5000` 🌐

## Project Structure 📂

The repository has the following structure:

```
media-dashboard/
├── Dockerfile
├── docker-compose.yaml
├── main.py
├── requirements.txt
└── templates
    └── index.html
```

- `Dockerfile`: Defines the Docker image for the Flask application
- `docker-compose.yaml`: Configures the Docker services and environment variables
- `main.py`: Contains the Flask application code and Home Assistant API integration
- `requirements.txt`: Lists the Python dependencies required for the project
- `templates/index.html`: Defines the HTML structure and layout of the Media Dashboard

## Technologies Used 🛠️

- Flask: Python web framework for building the application
- Flask-SocketIO: Library for enabling real-time communication between the client and server
- Home Assistant API: Integration with Home Assistant for retrieving media player data
- Docker: Containerization platform for easy deployment and portability

## Contributing 🤝

Contributions to the Media Dashboard project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request. Let's make this dashboard even better together! 😊

## License 📄

This project is licensed under the [MIT License](LICENSE).

---

Feel free to customize and enhance your media experience with the Media Dashboard! If you have any questions or need further assistance, don't hesitate to reach out. Happy media monitoring! 📻🎉
