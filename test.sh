export HEAD_REF="dev"
export BASE_REF="main"

if [ "$HEAD_REF" != "dev" ] && [ "$BASE_REF" == "main" ]; then
    echo "Merge requests to the main branch are only allowed from the dev branch."
    # gh run cancel ${{ github.run_id }}
    # gh run watch ${{ github.run_id }}
    exit 1
fi