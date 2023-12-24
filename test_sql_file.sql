-- SQLite
UPDATE ingredients_table
SET name = "null ingredient",
    desc = "empty ingredient",
    type = "ingredient",
    cost_per_unit = "0",
    cost_unit = "g"
WHERE
    id = 1