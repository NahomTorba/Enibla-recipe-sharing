# Enibla Recipe Sharing Platform

A modern recipe sharing platform built with Django, connecting food enthusiasts from around the world. Enibla provides a vibrant community where users can share, discover, and enjoy recipes from various cuisines.

## Features

### Core Features
- Create and share your own recipes
- Browse recipes from different cuisines
- Leave reviews and ratings
- Save favorite recipes
- Create and manage user profiles
- Responsive design for all devices

### Social Features
- Connect with other food lovers
- Rate and review recipes
- Save recipes on profile

### Advanced Features
- Recipe categorization by tags
- Recipe statistics and analytics
- Advanced search functionality
- Real-time recipe updates

## Technology Stack

- **Backend**: Django 5.2
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite3
- **Authentication**: Django Authentication System
- **Image Processing**: Pillow (PIL)
- **File Validation**: Django File Validators

## Dependencies

- Django
- Pillow
- Django Forms
- Django Messages
- Django Authentication
- Django Email Backend

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Pillow (for image processing)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/NahomTorba/Enibla-recipe-sharing.git
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application at `http://localhost:8000`

## Project Structure

```
enibla/
├── manage.py
├── requirements.txt
├── Enibla/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── App/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── urls.py
    ├── views.py
    └── templates/
        ├── auth/
        ├── profiles/
        └── recipes/
```

## Database Schema

### User Profile
- One-to-one relationship with Django User model
- Bio (500 characters)
- Favorite cuisines
- Profile image
- Creation and update timestamps

### Recipe
- Author (linked to UserProfile)
- Title and description
- Ingredients and instructions
- Tags (breakfast, lunch, dinner, etc.)
- Image upload
- Creation and update timestamps

### Review
- Recipe relationship
- User relationship
- Rating (1-5)
- Comment
- Creation timestamp

### Saved Recipe
- User relationship
- Recipe relationship
- Save timestamp

## API Endpoints

### Authentication
- `/auth/signup/` - User registration
- `/auth/login/` - User login
- `/auth/logout/` - User logout

### Recipes
- `/recipes/` - List all recipes
- `/recipes/create/` - Create new recipe
- `/recipes/<slug>/` - Recipe detail
- `/recipes/<slug>/edit/` - Edit recipe
- `/recipes/<slug>/delete/` - Delete recipe

### Reviews
- `/recipes/<pk>/review/` - Add review
- `/recipes/<pk>/reviews/` - List reviews

### Profile
- `/profile/` - Current user's profile
- `/profile/<username>/` - User profile
- `/profile/edit/` - Edit profile

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email [your-email@example.com](mailto:your-email@example.com) or create an issue in the repository.

## Future Development

- Implement recipe search by ingredients
- Add recipe video tutorials
- Implement recipe recommendations
- Add social sharing features
- Implement recipe nutrition information
- Add recipe planning features
- Implement recipe printing functionality
- Add recipe export/import features
- Implement recipe version control
- Add recipe collaboration features
