-- CREATE EXTENSION postgis;

CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    make VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    latitude VARCHAR(255) NOT NULL,
    longitude VARCHAR(255) NOT NULL,
    ownername VARCHAR(255) NOT NULL,
    mileage INTEGER NOT NULL,
    fuel_level VARCHAR(255) NOT NULL,
    temperature VARCHAR(255) NOT NULL,
    serviced_date DATE NOT NULL,
    next_service_date DATE,
    vehicle_alerts VARCHAR(255)[]
);

CREATE INDEX idx_vehicles_lat_lon
ON vehicles (latitude, longitude);

CREATE INDEX idx_vehicles_ownername
ON vehicles (ownername);

-- CREATE TABLE vehicles_new (
--     id SERIAL PRIMARY KEY,
--     make VARCHAR(255) NOT NULL,
--     model VARCHAR(255) NOT NULL,
--     gps_location POINT NOT NULL,
--     ownername VARCHAR(255) NOT NULL,
--     mileage INTEGER NOT NULL,
--     fuel_level VARCHAR(255) NOT NULL,
--     temperature VARCHAR(255) NOT NULL,
--     serviced_date DATE NOT NULL,
--     next_service_date DATE,
--     vehicle_alerts VARCHAR(255)[]
-- );

CREATE TABLE vehicles_locations (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(id), -- Assuming a 'vehicles' table
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- gps_location POINT NOT NULL,
    latitude NUMERIC,
    longitude NUMERIC,
    speed NUMERIC,
    mileage INTEGER NOT NULL,
    fuel_level INTEGER NOT NULL,
    temperature INTEGER NOT NULL,
    battery_level INTEGER NOT NULL,
    engine_status BOOLEAN,
    next_service_date DATE,
    vehicle_alerts VARCHAR(255)[]
);


-- CREATE TABLE vehicle_locations (
--     id SERIAL PRIMARY KEY,
--     vehicle_id INTEGER REFERENCES vehicles(id), -- Assuming a 'vehicles' table
--     timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--     location POINT NOT NULL,
--     speed NUMERIC,
--     direction NUMERIC,
--     battery_level NUMERIC,
--     engine_status BOOLEAN,
--     alerts VARCHAR(255)[]
-- );


-- CREATE TABLE vehicles (
--     id SERIAL PRIMARY KEY,
--     make VARCHAR(255) NOT NULL,
--     model VARCHAR(255) NOT NULL,
--     latitude VARCHAR(255) NOT NULL,
--     longitude VARCHAR(255) NOT NULL,
--     ownername VARCHAR(255) NOT NULL,
--     mileage INTEGER NOT NULL,
--     fuel_level VARCHAR(255) NOT NULL,
--     temperature VARCHAR(255) NOT NULL,
--     serviced_date DATE NOT NULL,
--     next_service_date DATE,
--     vehicle_alerts VARCHAR(255)[]
-- );

-- CREATE TABLE vehicles (
--     id SERIAL PRIMARY KEY,
--     make VARCHAR(255) NOT NULL,
--     model VARCHAR(255) NOT NULL,
--     latitude NUMERIC NOT NULL,
--     longitude NUMERIC NOT NULL,
--     ownername VARCHAR(255) NOT NULL,
--     mileage INTEGER NOT NULL,
--     fuel_level VARCHAR(255) NOT NULL,
--     temperature VARCHAR(255) NOT NULL,
--     serviced_date DATE NOT NULL,
--     next_service_date DATE,
--     vehicle_alerts VARCHAR(255)[]
-- );

-- ALTER TABLE vehicles
-- ALTER COLUMN latitude TYPE NUMERIC,
-- ALTER COLUMN longitude TYPE NUMERIC,
-- ADD COLUMN location POINT;
--
-- ALTER TABLE vehicles
-- ADD COLUMN location POINT;
--
--
-- UPDATE vehicles
-- SET location = ST_MakePoint(longitude, latitude);
--
-- UPDATE vehicles
-- SET location = ST_MakePoint(longitude::numeric, latitude::numeric);
--
-- CREATE INDEX idx_vehicles_location ON vehicles USING GIST (gps_location);
--
-- SELECT *
-- FROM vehicles
-- ORDER BY location <-> ST_MakePoint(your_longitude, your_latitude)::geography
-- LIMIT 5;

CREATE TABLE car_models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    generations INTEGER,
    sold_units INTEGER,
    in_stock_units INTEGER,
    damaged_units INTEGER,
    manufacturer VARCHAR(255),
    year_first_released INTEGER,
    body_type VARCHAR(255),
    engine_type VARCHAR(255),
    fuel_type VARCHAR(255),
    transmission_type VARCHAR(255),
    price_range NUMERIC,
    safety_rating VARCHAR(255),
    features TEXT  -- Store additional features as JSON or text
);

CREATE TABLE owners (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(255),
    department VARCHAR(255),
    hire_date DATE,
    salary NUMERIC
);

CREATE TABLE car_sales (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES car_models(id), -- Assuming a 'car_models' table
    color VARCHAR(255),
    vin_number VARCHAR(255) UNIQUE,
    sold_date DATE,
    latitude VARCHAR(255) NOT NULL,
    longitude VARCHAR(255) NOT NULL,
    dealer_name VARCHAR(255),
    list_price NUMERIC,
    sale_price NUMERIC,
    on_loan BOOLEAN,
    paid_cash BOOLEAN,
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20),
    salesperson_id INTEGER REFERENCES employees(id) -- Assuming an 'employees' table
);

CREATE TABLE dealers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(255),
    country VARCHAR(255),
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    website VARCHAR(255)
);

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    type VARCHAR(255) NOT NULL, -- 'car', 'airplane', 'drone', etc.
    name VARCHAR(255),
    description TEXT,
    availability BOOLEAN,
    units_in_stock INTEGER,
    cost NUMERIC,
    latitude VARCHAR(255) NOT NULL,
    longitude VARCHAR(255) NOT NULL,
    dealer_id INTEGER REFERENCES dealers(id), -- Assuming a 'dealers' table
    discount NUMERIC,
    promotion_code VARCHAR(255)
);

-- SELECT o.name AS owner_name, v.make, v.model, o.email, o.phone, v.vehicle_alerts, v.next_service_date
-- FROM owners o
-- INNER JOIN vehicles v ON o.name = v.ownername;
--
-- SELECT o.name AS owner_name, v.make, v.model, o.email, o.phone, v.vehicle_alerts, v.next_service_date
-- FROM owners o
-- INNER JOIN vehicles v ON o.name = v.ownername where vehicle_alerts != '{NULL}';


-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_name = 'vehicles';
--
-- INSERT INTO vehicles (make, model, latitude, longitude, ownername, mileage, fuel_level, temperature, serviced_date, next_service_date, vehicle_alerts)
-- VALUES (%s, %s, %s::numeric, %s::numeric, %s, %s, %s, %s, %s, %s, %s);
--
-- UPDATE vehicles
-- SET latitude = latitude::numeric;
