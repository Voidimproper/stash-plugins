#!/usr/bin/env bash

dry=false
dl=false
gen=false
models=(stash-box stats  scalar file performer gallery gallery-chapter scene studio tag)

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry) dry=true && echo "Dry run enabled" ;;
    --dl) dl=true && echo "Download enabled" ;;
    --gen) gen=true && echo "Generation enabled" ;;
    *) echo "Unknown option: $1" ; exit 1 ;;
  esac
  shift
done

stash_models_dir=plugins/void_common/models/stash
stash_graphql_dir=resources/graphql/types

mkdir -p "$stash_models_dir" "$stash_graphql_dir"

schema_types=($(gh api \
  -H "Accept: application/vnd.github.json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/stashapp/stash/contents/graphql/schema/types \
  | jq '.[] | select(.type == "file") | .download_url'))

schema_base=($(gh api \
  -H "Accept: application/vnd.github.json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/stashapp/stash/contents/graphql/schema \
  | jq '.[] | select(.type == "file") | .download_url'))

codegen(){
  gql_file=$(find "$stash_graphql_dir" -name $(basename "${1})")
  schema_name=$(echo "${1}" | sed -E 's/\.graphql//g')
  output="${stash_models_dir}/${schema_name}.py"
  class_name=$(echo "${schema_name}" | awk '{ print toupper(substr($0,1,1))substr($0,2) }')Model

  opts='--input-file-type graphql --use-standard-collections'

  if [ "$dry" = true ]; then
    echo "datamodel-codegen --input $gql_file $opts --output $output --class-name $class_name"
    echo "Dry run, skipping code generation"
    return 0
  fi

  datamodel-codegen --input "$gql_file" "$opts" --output "$output" --class-name "$class_name"
}

download(){
  if [ "$dry" = true ]; then
    echo "curl -sL ${1} -o $stash_graphql_dir/$(basename ${1})"
    echo "Dry run, skipping download of ${1}"
    return 0
  fi
  curl -sL "${1}" -o "$stash_graphql_dir/$(basename ${1})"
}

for schema in "${schema_types[@]}"; do
  schema_url=$(echo "$schema" | tr -d '"')
  echo "Processing: $(basename ${schema_url})"
  if [ "$dl" = true ]; then
    download "${schema_url}"
  fi
  if [ "$gen" = true ]; then
    codegen "$(basename ${schema_url})"
  fi
done
