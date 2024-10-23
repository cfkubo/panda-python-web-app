-- CREATE SEQUENCE vehicles_seq
--   START WITH 1
--   INCREMENT BY 1
--   NOCACHE;

CREATE TABLE vehicles (
  id NUMBER GENERATED ALWAYS AS IDENTITY,
  make VARCHAR2(255) NOT NULL,
  model VARCHAR2(255) NOT NULL,
  latitude VARCHAR2(255) NOT NULL,
  longitude VARCHAR2(255) NOT NULL,
  ownername VARCHAR2(255) NOT NULL,
  mileage NUMBER NOT NULL,
  fuel_level VARCHAR2(255) NOT NULL,
  temperature VARCHAR2(255) NOT NULL,
  serviced_date DATE NOT NULL,
  next_service_date DATE,
  vehicle_alerts VARCHAR2(4000)
);


CREATE TABLE car_models (
    id NUMBER GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    generations NUMBER,
    sold_units NUMBER,
    in_stock_units NUMBER,
    damaged_units NUMBER,
    manufacturer VARCHAR(255),
    year_first_released NUMBER,
    body_type VARCHAR(255),
    engine_type VARCHAR(255),
    fuel_type VARCHAR(255),
    transmission_type VARCHAR(255),
    price_range NUMERIC,
    safety_rating VARCHAR(255),
    features VARCHAR2(4000)  -- Store additional features as JSON or text
);


CREATE TABLE employees (
    id NUMBER GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(255),
    department VARCHAR(255),
    hire_date DATE,
    salary NUMBER
);

CREATE TABLE owners (
    id NUMBER GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address VARCHAR2(4000)
);
