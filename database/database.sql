CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE category (
	category_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
	name VARCHAR(1000) NOT NULL, 
	version_id VARCHAR(32) NOT NULL
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE UNIQUE INDEX ix_category_category_id ON category (category_id);
CREATE UNIQUE INDEX ix_category_name ON category (name);
CREATE TABLE list (
	list_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
	name VARCHAR(1000) NOT NULL, 
	version_id VARCHAR(32) NOT NULL
);
CREATE UNIQUE INDEX ix_list_list_id ON list (list_id);
CREATE UNIQUE INDEX ix_list_name ON list (name);
CREATE TABLE user (
	user_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
	email VARCHAR(1000) NOT NULL, 
	password_hash VARCHAR(128) NOT NULL, 
	active BOOLEAN NOT NULL, 
	updated_on DATETIME NOT NULL, 
	version_id VARCHAR(32) NOT NULL, 
	CHECK (active IN (0, 1))
);
CREATE UNIQUE INDEX ix_user_email ON user (email);
CREATE UNIQUE INDEX ix_user_user_id ON user (user_id);
CREATE TABLE item (
	item_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
	name VARCHAR(1000) NOT NULL, 
	version_id VARCHAR(32) NOT NULL, 
	category_id INTEGER NOT NULL, 
	FOREIGN KEY(category_id) REFERENCES category (category_id) ON DELETE RESTRICT, 
	UNIQUE (name, category_id)
);
CREATE INDEX ix_item_category_id ON item (category_id);
CREATE UNIQUE INDEX ix_item_item_id ON item (item_id);
CREATE INDEX ix_item_name ON item (name);
CREATE TABLE list_item (
	list_id INTEGER NOT NULL, 
	item_id INTEGER NOT NULL, 
	type VARCHAR(9) NOT NULL, 
	selection BOOLEAN, 
	counter INTEGER, 
	text VARCHAR(1000), 
	version_id VARCHAR(32) NOT NULL, 
	PRIMARY KEY (list_id, item_id), 
	FOREIGN KEY(item_id) REFERENCES item (item_id) ON DELETE CASCADE, 
	FOREIGN KEY(list_id) REFERENCES list (list_id) ON DELETE CASCADE, 
	CONSTRAINT listitemtype CHECK (type IN ('none', 'selection', 'counter', 'text')), 
	CHECK (selection IN (0, 1))
);
CREATE INDEX ix_list_item_item_id ON list_item (item_id);
CREATE INDEX ix_list_item_list_id ON list_item (list_id);
