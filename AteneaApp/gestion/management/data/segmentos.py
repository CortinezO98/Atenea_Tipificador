segmentos = [
    # CHAT
    {
        "id": 17,
        "nombre": "Chat",
        "tipo_canal_id": 1,  # CHAT
        "tiene_segmento_ii": False
    },
    
    # SMS
    {
        "id": 18,
        "nombre": "SMS",
        "tipo_canal_id": 2,  # SMS
        "tiene_segmento_ii": False
    },
    
    # INBOUND
    {
        "id": 19,
        "nombre": "NIVEL I",
        "tipo_canal_id": 3,  # INBOUND
        "tiene_segmento_ii": False,
        "activo": False
    },
    {
        "id": 20,
        "nombre": "NIVEL II",
        "tipo_canal_id": 3,  # INBOUND
        "tiene_segmento_ii": False,
        "activo": False
    },
    {
        "id": 21,
        "nombre": "BILINGÜE",
        "tipo_canal_id": 3,  # INBOUND
        "tiene_segmento_ii": True  # Necesita Segmento II
    },
    {
        "id": 22,
        "nombre": "PSICOLOGIA",
        "tipo_canal_id": 3,  # INBOUND
        "tiene_segmento_ii": True  # Necesita Segmento II
    },
    
    # OUTBOUND
    {
        "id": 23,
        "nombre": "NIVEL I",
        "tipo_canal_id": 4,  # OUTBOUND
        "tiene_segmento_ii": False,
        "activo": False
    },
    {
        "id": 24,
        "nombre": "NIVEL II",
        "tipo_canal_id": 4,  # OUTBOUND
        "tiene_segmento_ii": False,
        "activo": False
    },
    {
        "id": 25,
        "nombre": "BILINGÜE",
        "tipo_canal_id": 4,  # OUTBOUND
        "tiene_segmento_ii": True
    },
    {
        "id": 26,
        "nombre": "PSICOLOGIA",
        "tipo_canal_id": 4,  # OUTBOUND
        "tiene_segmento_ii": True
    },
    
    # VIRTUAL HOLD
    {
        "id": 27,
        "nombre": "NIVEL I",
        "tipo_canal_id": 5,  # VIRTUAL HOLD
        "tiene_segmento_ii": False,
        "activo": False
    },
    {
        "id": 28,
        "nombre": "NIVEL II",
        "tipo_canal_id": 5,  # VIRTUAL HOLD
        "tiene_segmento_ii": False,
        "activo": False
    },
    {
        "id": 29,
        "nombre": "BILINGÜE",
        "tipo_canal_id": 5,  # VIRTUAL HOLD
        "tiene_segmento_ii": True
    },
    {
        "id": 30,
        "nombre": "PSICOLOGIA",
        "tipo_canal_id": 5,  # VIRTUAL HOLD
        "tiene_segmento_ii": True
    },
    
    # VIDEO LLAMADA
    {
        "id": 31,
        "nombre": "PERSONA OYENTE",
        "tipo_canal_id": 6,  # VIDEO LLAMADA
        "tiene_segmento_ii": False
    },
    {
        "id": 32,
        "nombre": "PERSONA NO OYENTE",
        "tipo_canal_id": 6,  # VIDEO LLAMADA
        "tiene_segmento_ii": False
    },

    # INBOUND
    {
        "id": 33,
        "nombre": "DELITOS PRIORIZADOS",
        "tipo_canal_id": 3,  # INBOUND
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 34,
        "nombre": "DELITOS COMUNES",
        "tipo_canal_id": 3,  # INBOUND
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 35,
        "nombre": "AMPLIACIÓN DE INCIDENTES",
        "tipo_canal_id": 3,  # INBOUND
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 36,
        "nombre": "ORIENTACIONES",
        "tipo_canal_id": 3,  # INBOUND
        "tiene_segmento_ii": False,
        "activo": True
    },

    # OUTBOUND
    {
        "id": 37,
        "nombre": "DELITOS PRIORIZADOS",
        "tipo_canal_id": 4,  # OUTBOUND
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 38,
        "nombre": "DELITOS COMUNES",
        "tipo_canal_id": 4,  # OUTBOUND
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 39,
        "nombre": "AMPLIACIÓN DE INCIDENTES",
        "tipo_canal_id": 4,  # OUTBOUND
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 40,
        "nombre": "ORIENTACIONES",
        "tipo_canal_id": 4,  # OUTBOUND
        "tiene_segmento_ii": False,
        "activo": True
    },

    # VIRTUAL HOLD
    {
        "id": 41,
        "nombre": "DELITOS PRIORIZADOS",
        "tipo_canal_id": 5,  # VIRTUAL HOLD
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 42,
        "nombre": "DELITOS COMUNES",
        "tipo_canal_id": 5,  # VIRTUAL HOLD
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 43,
        "nombre": "AMPLIACIÓN DE INCIDENTES",
        "tipo_canal_id": 5,  # VIRTUAL HOLD
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 44,
        "nombre": "ORIENTACIONES",
        "tipo_canal_id": 5,  # VIRTUAL HOLD
        "tiene_segmento_ii": False,
        "activo": True
    },

    # LLAMADA VIRTUAL
    {
        "id": 45,
        "nombre": "DELITOS PRIORIZADOS",
        "tipo_canal_id": 7,  # LLAMADA VIRTUAL
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 46,
        "nombre": "DELITOS COMUNES",
        "tipo_canal_id": 7,  # LLAMADA VIRTUAL
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 47,
        "nombre": "AMPLIACIÓN DE INCIDENTES",
        "tipo_canal_id": 7,  # LLAMADA VIRTUAL
        "tiene_segmento_ii": False,
        "activo": True
    },
    {
        "id": 48,
        "nombre": "ORIENTACIONES",
        "tipo_canal_id": 7,  # LLAMADA VIRTUAL
        "tiene_segmento_ii": False,
        "activo": True
    },

    #Nuevo segmento en inbound
    {
        "id": 49,
        "nombre": "AGENTE FILTRO",
        "tipo_canal_id": 3,  # INBOUND
        "tiene_segmento_ii": False  
    },
]