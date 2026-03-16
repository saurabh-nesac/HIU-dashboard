$ROOT="rainfall_system"

$dirs=@(
"data/wrf_raw",
"data/rainfall",
"data/rgba_tif",
"tiles",
"backend/ingest",
"backend/processing",
"backend/tiling",
"backend/api",
"frontend/js",
"frontend/css",
"scripts",
"config"
)

foreach($d in $dirs){

New-Item -ItemType Directory -Force -Path "$ROOT/$d"
}