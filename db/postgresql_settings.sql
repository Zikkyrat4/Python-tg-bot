CREATE USER repl_user REPLICATION LOGIN PASSWORD 'Qq12345';

CREATE DATABASE info;

\c info;

CREATE TABLE IF NOT EXISTS phone_numbers (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL
);

COPY emails (id, email) FROM stdin;
1	test1@example.com
2	test2@example.com
3	lisasunshine@gmail.com
4	jakeadventure@gmail.com
5	emilydreamer@gmail.com
6	maxthegreat@gmail.com
7	katewonderland@gmail.com
8	tomcat@gmail.com
9	annastarlight@gmail.com
10	lukefire@gmail.com
11	olivialovesanimals@gmail.com
12	joshuaadventurer@gmail.com
\.



COPY phone_numbers (id, phone_number) FROM stdin;
1814	8 (987) 653-21-00 
1815	8 (888) 888-88-88
1816	8 (888) 888-85-885
1817	8 (888) 888-88-777
1818	82134323443
1819	8(678)7856743
1820	8 781 213 32 23 
1821	8-913-123-90-34
1822	+79531238435
\.
