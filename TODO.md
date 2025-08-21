# lpo-measure
- [x] Add multiprocessing. We should run N cases in parallel. hardcode N=3 as a global var
- [x] There is a bug when adding cases. Even new cases report that the file already exists. Verify and fix.
- [x] Commit message from clay into run schema, pass as input param
- [ ] Switch on output db, local stuff goes to a dev db, only ci writes runs to prod db.
- [ ] Finish the ci runner. Runs that are written to prod db are commited to the repo. Make a nice commit message.
- [ ] Think about how much context the judge sysprompt should have about clay
- [ ] Build a dashboard using Panel
- [ ] Compile dashboard to static html + js as shown in https://panel.holoviz.org/how_to/wasm/convert.html, and host in github pages
- [ ] Pricing info. A measurement report should also contain information about the total cost of the measurement, using the litellm api.

# electron-terminal (clay)
The following TODOs cannot be solved in this repo, so leave them be. They are related notes for me.
- [ ] Pass in correct state format for full multi-canvas state
- [ ] Fix ability to run against any commit
- [ ] CI workflow to do an integration test that does not push to prod db
- [ ] Correct canvas for initial state, with a chat node present
