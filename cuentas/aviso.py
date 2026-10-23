"""Texto y versión del aviso mostrado al solicitar una cuenta."""

AVISO_DATOS_VERSION = "1.0"

AVISO_DATOS_SECCIONES = (
    (
        "Proyecto y equipo a cargo",
        "Huertos medicinales comunitarios es un proyecto académico del equipo "
        "Nova Alexandria para la asignatura Calidad de Software de la EPN. "
        "El equipo está a cargo del desarrollo y mantenimiento de la aplicación.",
    ),
    (
        "Datos solicitados",
        "Solicitamos usuario, contraseña, nombre completo y fecha de nacimiento. "
        "Puedes dejar sin indicar el género y los talentos ancestrales. "
        "La contraseña se guarda mediante el sistema de hash de Django; "
        "no se conserva su texto original.",
    ),
    (
        "Para qué se utilizan",
        "Los datos permiten identificar tu cuenta, participar en una comunidad, "
        "registrar tus actividades y mostrar los puntos y niveles del proyecto. "
        "La información de las plantas tiene una finalidad educativa.",
    ),
    (
        "Visibilidad de la información",
        "Los miembros de tu comunidad pueden consultar tu nombre, puntos y nivel. "
        "El acceso a tu fecha de nacimiento y género se reserva a tu propia "
        "cuenta en las pantallas de la aplicación, también frente al responsable "
        "de la comunidad.",
    ),
    (
        "Almacenamiento y consultas",
        "La aplicación utiliza una base de datos local. El equipo de desarrollo "
        "puede acceder a ella para las tareas de mantenimiento y demostración. "
        "Las pruebas y demostraciones del proyecto se realizan con datos ficticios. "
        "Puedes dirigirte al equipo Nova Alexandria para consultar el uso de tus "
        "datos o solicitar una corrección.",
    ),
    (
        "Aceptación del aviso",
        "Crear la cuenta requiere que leas y aceptes este aviso. Guardamos la "
        "fecha, la hora y la versión que aceptaste. No se registra una aceptación "
        "por defecto. El aviso también debe permanecer consultable desde tu perfil.",
    ),
)
