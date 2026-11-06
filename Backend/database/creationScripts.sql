--CREATING THE PLANS TABLE
create table plans(
 id varchar(20) primary key,
 name varchar(20),
 price float,
 billing_interval varchar(20),
 trial_days int,
 features clob,
 created_at date,
 updated_at DATE,
 status varchar(20) DEFAULT 'active'
 );

SELECT *FROM plans;
--CREATING THE CUSTOMERS TABLE
CREATE TABLE customers(
customer_id varchar(20) PRIMARY KEY ,
	name varchar(30),
	email varchar(40),
	created_at DATE ,
	updated_at DATE,
	password varchar(30)
);

--CREATING THE SUBSCRIPTIONS TABLE
CREATE TABLE subscriptions(
	subscription_id varchar(20) PRIMARY key,
	customer_id varchar(20),
	plan_id varchar(20),
	status varchar(20),
	start_date DATE,
	end_date DATE,
	created_at DATE,
	updated_at date
);

--CREATING THE BILLING_CYCLES TABLE
CREATE TABLE billing_cycles(
	subscription_id varchar(20),
	cycle_start_date DATE,
	cycle_end_date DATE,
	renewal_date DATE,
	status varchar(20),
	created_at DATE,
	updated_at DATE,
	CONSTRAINT chk_billing_cycle_status
        CHECK (status IN ('pending', 'completed','cancelled'))
);

--CREATING INVOINCE TABLE
CREATE TABLE invoice(
	invoice_id varchar(20),
	subscription_id varchar(20),
	customer_id varchar(20),
	invoice_date DATE,
	due_date DATE,
	subtotal float,
	tax_amount float,
	total_amount float,
	status varchar(10),
	CONSTRAINT chk_invoice_status check(status IN ('draft','paid','unpaid','void'))
);

--CREATING PAYMENT TABLE
CREATE TABLE payment(
	invoice_id varchar(20),
	payment_reference varchar(20),
	amount float,
	payment_method varchar(20),
	status varchar(15) check(status IN('pending','failed','success','refunded')),
	payment DATE,
	cretaed_at DATE,
	updated_at DATE
);

--CREATING AUDIT LOGS TABLE
CREATE TABLE audit_logs(
	entity_type varchar(20),
	entity_id varchar(20),
	action varchar(30),
	old_value clob,
	new_value clob,
	performed_by varchar(100),
	created_at date
);

--IMPORTING SOME RANDOM DATA INTO PLANS TABLE
INSERT INTO plans (
    id,
    name,
    billing_interval,
    trial_days,
    features,
    created_at,
    updated_at
) VALUES (
    'PLAN-002',   
    'Basic Plan',
    'MONTHLY',
    15,
    '{"features": ["Unlimited projects", "Priority support", "Advanced analytics"]}',
    SYSDATE,
    SYSDATE
);
INSERT INTO plans (
    id,
    name,
    price,
    billing_interval,
    trial_days,
    features,
    created_at,
    updated_at
) VALUES (
    'PLAN-002',
    'Advanced',
    500,
    'Yearly',
    14,
    '{"features": ["Unlimited projects", "Priority support", "Advanced analytics"]}',
    SYSDATE,
    SYSDATE
);

ALTER TABLE subscriptions
ADD CONSTRAINT fk_subscription_customer
FOREIGN KEY (customer_id)
REFERENCES customers(customer_id);

ALTER TABLE subscriptions
ADD CONSTRAINT fk_subscription_plans
FOREIGN KEY (plan_id)
REFERENCES plans(id);



ALTER TABLE invoice
ADD CONSTRAINT fk_subscription_customers
FOREIGN KEY (customer_id)
REFERENCES customers(customer_id);


SELECT *FROM customers;

SELECT *FROM invoice;
SELECT *FROM plans;

SELECT *FROM subscriptions;
SELECT *FROM billing_cycles;
SELECT *FROM audit_logs;













