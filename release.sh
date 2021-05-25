#!/bin/bash

# Script to simplify the release flow
# 1) Fetch the current release version
# 2) Increase the version (major, minor, patch)
# 3) Checkout develop branch if current branch is not develop branch
# 4) Create a new release branch off develop branch
# 5) Run command for merging origin/master to release branch

# Parse command line options.
while getopts ":Mmpd" Option
do
  case $Option in
    M ) major=true;;
    m ) minor=true;;
    p ) patch=true;;
    d ) dry=true;;
  esac
done

shift $(($OPTIND - 1))

# Display usage
if [ -z $major ] && [ -z $minor ] && [ -z $patch ] && [-z $dry];
then
  echo "usage: $(basename $0) [Mmp] [message]"
  echo ""
  echo "  -d Dry run"
  echo "  -M for a major release"
  echo "  -m for a minor release"
  echo "  -p for a patch release"
  echo ""
  echo " Example: release -p \"Some fix\""
  echo " means create a patch release with the message \"Some fix\""
  exit 1
fi

# 1) Fetch the current release version

echo "Fetch tags"
git fetch --prune --tags

version=$(git describe --tags $(git rev-list --tags --max-count=1))

echo "Current version: $version"

# 2) Increase version number

# Build array from version string.

a=( ${version//./ } )

# Increment version numbers as requested.

if [ ! -z $major ]
then
  ((a[0]++))
  a[1]=0
  a[2]=0
fi

if [ ! -z $minor ]
then
  ((a[1]++))
  a[2]=0
fi

if [ ! -z $patch ]
then
  ((a[2]++))
fi

next_version="${a[0]}.${a[1]}.${a[2]}"

username=$(git config user.name)
msg="$1 by $username"

# If its a dry run, just display the new release version number
echo "Next version: $next_version"
if [ ! -z $dry ]
then
  echo "Tag message: $msg"
  echo "Next version: $next_version"
else
  # If a command fails, exit the script
  set -e

  # current Git branch
  branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

  # if current branch is not develop branch
  if [[ $branch != "development" ]]
  then
    git checkout development
    git pull
  fi

  # establish branch variables
  releaseBranch=release/$next_version

  # create the release branch from the -develop branch
  git checkout -b $releaseBranch
  # merge master to release branch
  git merge --no-ff origin/master

fi