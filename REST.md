### API endpoints
- __```/historical/```__
  - GET
    - Fetch list of all dates for which weather information is available
    - Response: 200
    - Response type: *application/json*
      ```
      [{"DATE": "20130101"},
      {"DATE": "20130102"},
      ...
      {"DATE": "20170115"}
      ```
  - POST
    - Add weather info for a particular date
    - Input parameter type: *application/json*
    - Input parameter:
    ```
    {
      "DATE": "string",
      "TMAX": "string",
      "TMIN": "string"
    }
    ```
    - Response: 201
    - Response type: *application/json*
      ```
      {"DATE": "20130101"}
      ```
- __```/historical/{DATE}```__
  - GET
    - Fetch weather information for a particular date
    - Response: 200
    - Response type: *application/json*
      ```
      {"DATE": "20130101",
      "TMAX": "34.0",
      "TMIN": "26.0"}
      ```
  - DELETE
    - Delete weather date for a particular date
    - Response: 200
- __```/forecast/{DATE}```__
  - GET
    - Fetch weather forecast for the next 7 days
    - Response: 200
    - Response type: *application/json*
    ```
    [{"DATE":"YYYYMMDD","TMAX":"xx.yy","TMIN":"xx.yy"},
      ...
    ]
    ```
