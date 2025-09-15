# mtl-api

This is supposed to be the backend for mtl app. The purpose of this app is to be able to help with managing trips and payroll for a logistics company. There are several things to consider but l will try to build from the top down. For now things like permissions will take a back burner and l will just build the core 
function. As l build l will make them blocky so that they can be intergreated easily as we build more and more. 

## Goals 
- Trip Class and all the methods that come with it 
    - CRUD (Create, Update, Delete, Read) Trip
    - upload receipts pdf or picture 
    - autofill in details needed and ask for missing detail (client or server side)? 
    - Calculate dead head miles 
    - Calculate earnings per mile 
    - driver assignment etc

- Calculate Earnings for driver and company
    - From details of trip auto update the Earnings for the driver etc 
    - Will define better as we go 

- Also make the app such that for those who would want to self deploy/host 
it is easy 
- For those who want our hosting we can do it as well the business case figured out later for sure. 

Will get more requirements later as we go. 


## Endpoints and Their Explanations 

### Trips

`GET /api/trips/` This will get all the trips 


#### Getting trips with filters
`GET /api/trips/?status=Scheduled ` This will get all the trips that have status as Scheduled
```
broker
rate_con_number
rate
pickup_location
dropoff_location
pickup_date
delivery_date
status
created_at
updated_at
driver_id    # Get trip by a particular driver
truck_id     # Get trips by a particular truck
```

- Update also works for all this 
- Trip Status 
    - Load Status 
    - Truck Status 


### Trucks

- Get all trucks 
- Get truck location
- 



