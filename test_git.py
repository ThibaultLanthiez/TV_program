from git import Repo

repo = Repo(".git")
repo.git.add(update=True)
repo.index.commit('script')
origin = repo.remote(name='origin')
origin.push()
