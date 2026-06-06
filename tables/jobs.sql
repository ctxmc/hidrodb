CREATE TABLE [Chuvas]
(
    [ID]        AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [ResumoDescarga]
(
    [ID]        AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [Sedimentos]
(
    [ID]        AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [QualAgua]
(
    [ID]        AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);

CREATE TABLE [Cotas]
(
    [ID]        AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);
