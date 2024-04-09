-- SWAMI KARUPPASWAMI THUNNAI
create database if not exists genesis;
use genesis;
create table if not exists hospital_employee(
    id bigint(20) primary key auto_increment,
    username varchar(20) unique,
    password char(128),
    role varchar(20)
);
create table if not exists patient (
    id bigint(20) primary key auto_increment,
    phone varchar(10) unique key,
    name text,
    father_name text,
    dob date,
    gender tinyint(1),
    address text,
    drug_allergy text,
    family_history text,
    added_by bigint(20),
    created_on timestamp default current_timestamp
);
create table if not exists ticket_counter (
    id bigint(20) primary key auto_increment,
    patient_id bigint(20),
    nadi FLOAT,
    patient_height float,
    patient_weight float,
    patient_temperature float,
    spo2 float,
    bp int,
    admission_date timestamp default current_timestamp,
    consulted tinyint(1) default 0,
    food_restrictions text,
    present_complaint text,
    diagnosis text,
    therapy text,
    medicines text,
    added_by bigint(20),
    created_on timestamp default current_timestamp
);
create table if not exists medicine (
    id bigint(20) primary key auto_increment,
    name varchar(20),
    med_type text,
    manufacturer text,
    description text,
    added_by bigint(20),
    created_on timestamp default current_timestamp
);
create table if not exists prescription(
    id bigint(20) primary key auto_increment,
    patient_id bigint(20),
    info json,
    description text,
    added_by bigint(20),
    created_on timestamp default current_timestamp
);