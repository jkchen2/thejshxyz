MESSAGE = Auto-generated commit
CNAME = thejsh.xyz

.PHONY: deploy build devsvg

deploy: build
	@echo "Deploying..."
	angular-cli-ghpages --no-silent --message="${MESSAGE}"
	@echo "Deployment complete."

build:
	@echo "Building..."
	ng build --prod --base-href "/"
	python build/og_generate.py
	python build/svg_generate.py
	echo "${CNAME}" > dist/CNAME
	@echo "Build complete."

devsvg: 
	@echo "Updating SVG for development..."
	python build/svg_generate.py dev
	@echo "Updated."
