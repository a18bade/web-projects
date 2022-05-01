CREATE TABLE user_info (
  user_id SERIAL PRIMARY KEY,
  nickname text UNIQUE,
  email text UNIQUE
);

CREATE TABLE score (
  score_id SERIAL PRIMARY KEY,
  nickname text REFERENCES user_info (nickname),
  dateplay timestamp,
  course text,
  score int,
  strokes int
);

CREATE TABLE courses (
  state text,
  course text,
  holeList text,
  parList text
);
