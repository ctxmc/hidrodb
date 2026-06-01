CREATE TABLE [Rain]
(
    [ID]        AUTOINCREMENT,
    [StationID] Long NOT NULL,
    [FromDate]  DateTime NOT NULL,
    [ToDate]    DateTime NOT NULL,
    [Status]    Byte NOT NULL
);
