CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE list (
	list_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
	name VARCHAR(1000) NOT NULL, 
	created_by INTEGER NOT NULL, 
	private BOOLEAN NOT NULL, 
	version_id VARCHAR(32) NOT NULL
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE UNIQUE INDEX ix_list_list_id ON list (list_id);
CREATE UNIQUE INDEX ix_list_name ON list (name);
CREATE TABLE user (
	user_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
	email VARCHAR(1000) NOT NULL, 
	password_hash VARCHAR(128) NOT NULL, 
	active BOOLEAN NOT NULL, 
	updated_on DATETIME NOT NULL, 
	version_id VARCHAR(32) NOT NULL
);
CREATE UNIQUE INDEX ix_user_email ON user (email);
CREATE UNIQUE INDEX ix_user_user_id ON user (user_id);
CREATE TABLE category (
	category_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
	name VARCHAR(1000) NOT NULL, 
	version_id VARCHAR(32) NOT NULL, 
	list_id INTEGER NOT NULL, 
	FOREIGN KEY(list_id) REFERENCES list (list_id), 
	UNIQUE (list_id, name)
);
CREATE UNIQUE INDEX ix_category_category_id ON category (category_id);
CREATE INDEX ix_category_list_id ON category (list_id);
CREATE INDEX ix_category_name ON category (name);
CREATE TABLE item (
	item_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
	name VARCHAR(1000) NOT NULL, 
	type VARCHAR(9) NOT NULL, 
	selection BOOLEAN NOT NULL, 
	number VARCHAR(1000) NOT NULL, 
	text VARCHAR(1000) NOT NULL, 
	version_id VARCHAR(32) NOT NULL, 
	category_id INTEGER NOT NULL, 
	FOREIGN KEY(category_id) REFERENCES category (category_id), 
	UNIQUE (category_id, name)
);
CREATE INDEX ix_item_category_id ON item (category_id);
CREATE UNIQUE INDEX ix_item_item_id ON item (item_id);
CREATE INDEX ix_item_name ON item (name);
