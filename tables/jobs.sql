CREATE TABLE [Chuvas]
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [ResumoDescarga]
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [Sedimentos]
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [QualAgua]
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [Cotas]
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [CurvaDescarga]
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [Granulometria]
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [PerfilTransversal]
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [Telemeter]
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [Date]      DateTime NOT NULL,
    [Interval]  Byte NOT NULL,
    [Status]    Byte NOT NULL
);

