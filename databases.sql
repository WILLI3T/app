---Users Table Schema 
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true
);

ALTER SEQUENCE Users_user_id_seq RESTART WITH 100;
ALTER SEQUENCE Users_user_id_seq INCREMENT BY 1;
ALTER SEQUENCE Users_user_id_seq MAXVALUE 1999;

CREATE TABLE Roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(255) UNIQUE NOT NULL
);

ALTER SEQUENCE Roles_role_id_seq RESTART WITH 1;
ALTER SEQUENCE Roles_role_id_seq INCREMENT BY 1;
ALTER SEQUENCE Roles_role_id_seq MAXVALUE 99;

CREATE TABLE UserRoles (
    user_role_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id) 
        REFERENCES Users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_role
        FOREIGN KEY(role_id) 
        REFERENCES Roles(role_id)
        ON DELETE CASCADE
);

ALTER SEQUENCE UserRoles_user_role_id_seq RESTART WITH 2000;
ALTER SEQUENCE UserRoles_user_role_id_seq INCREMENT BY 1;
ALTER SEQUENCE UserRoles_user_role_id_seq MAXVALUE 3000;


