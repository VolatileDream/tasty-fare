# Components

There are two major components:
 * Food Management
 * Upc Lookup & Caching

Food
 - uniquely identified food items.
 - they have a name
 - department

Consumed - set of recently consumed Food
Groceries - set of food to buy
Shopping List - Department ordered list of Food

UpcMapping
 - mapping of many UPC to one Food

### Food
 * unique ID
 * Name
 * Department.ID | NULL

### Department / Category
 * unique ID
 * Name
 * prev: Department.id | NULL
 * next: Department.id | NULL

 - Items with no Department are in the "unknown" which is first.
 - There is a "[Trash]" department, which is last, and can not be deleted.
  - must be created with database setup.
 - `prev` and `next` are used to make it an ordered list with easy update semantics,
    instead of using a position numbering scheme.

### Consumed (set)
 * Food.ID

### Groceries (set)
 * Food.ID


### UpCMapping
 * unique UPC
 * Food.ID

NOTE: when querying for UPC with type Variable you must zero out the bottom bits & checksum.

# Routes

 * `/api/food` -> Food[]
  * All Food
  * GET
 * `/api/food` -> Food
  * PUT - new food
 * `/api/food/{id}` -> Food
  * GET & PATCH - edit
  * DELETE -> only moves food to "[Trash]" category

 * /api/categories -> Category[]
  * GET - category list
  * PUT - new category
 * /api/categories/{id}
  * GET, PATCH, DELETE

 * `/api/groceries` -> ?
  * Food to buy, grouped.
  * GET
 * `/api/groceries/{id}` -> ?
  * PUT / DELETE - add / remove items

 * `/api/consumed` -> ?
  * GET
 * `/api/consumed/{id | upc}
  * PUT / DELETE- add / remove items
  * PUT / DELETE - add / remove items using upc

 * `/api/upc/{id}` -> (upc, Food)
  * May canonicalize UPC (eg, variable codes), check return.
  * GET & PUT

 * `/` forwards to `/app`
 * `/app` - application home
 * `/app/...` - application sub pages
