ROBOT = robot # Set this to your local path (Need to switch this to take input!)

# JOBS = Quadriceps_Femoris Triceps_Surae White_Adipose  don't have data in table
# NEW TABLES NOT RELEASED YET: Mammary_Gland
JOBS = Anatomical_Systems Blood Bone-Marrow Brain Eye Fallopian_tube Heart Kidney Knee Large_intestine Liver Lung Lymph_node Lymph_vasculature Main_Bronchus Mammary_Gland Muscular_System Ovary Pancreas Palatine_Tonsil Peripheral_nervous_system Placenta Prostate Skeleton Skin Small_intestine Spinal_Cord Spleen Thymus Trachea Ureter Urinary_bladder Uterus Blood_vasculature
JOBS_OLD = Bone-Marrow Blood Brain Eye Fallopian_tube Heart Kidney Knee Large_intestine Liver Lung Lymph_node Lymph_vasculature Ovary Pancreas Placenta Peripheral_nervous_system Prostate Skin Small_intestine Spleen Thymus Ureter Urinary_bladder Uterus Blood_vasculature 
JOBS_MARKERS = Bone-Marrow Blood Brain Eye Fallopian_tube Heart Kidney Knee Large_intestine Liver Lung Lymph_node Lymph_vasculature Ovary Pancreas Placenta Peripheral_nervous_system Prostate Skin Small_intestine Spleen Thymus Ureter Urinary_bladder Uterus
OLD_VERSION = False

TODAY ?= $(shell date +%Y-%m-%d)
VERSION = $(TODAY)
CATALOG = --catalog catalog-v001.xml
OWL_CLASS_FILES_OLD = $(patsubst %, ../owl/last_official_ASCTB_release/ccf_%_classes.owl, $(JOBS_OLD))
OWL_ANNOTATION_FILES_OLD = $(patsubst %, ../owl/%_annotations.owl, $(JOBS_OLD))
OWL_CLASS_FILES = $(patsubst %, ../owl/ccf_%_classes.owl, $(JOBS))
OWL_CLASS_SEC_FILES = $(patsubst %, ../owl/%_sec_reduced.owl, $(JOBS))
OWL_ANNOTATION_FILES = $(patsubst %, ../owl/%_annotations.owl, $(JOBS))
OWL_UB_SUBSET_FILES = $(patsubst %, ../owl/ub_%_ASCTB_subset.owl, $(JOBS))
OWL_CL_SUBSET_FILES = $(patsubst %, ../owl/cl_%_ASCTB_subset.owl, $(JOBS))
JSON_CLASSES_SUBSET = $(patsubst %, ../owl/%_ASCTB_subset.json, $(JOBS))
CSV_CT_LOC_B = $(patsubst %, ../logs/ct_loc_markers/%_report.tsv, $(JOBS_MARKERS))

all: last_official_release official_release

../resources/ASCT-b_tables/%.json:
	python download_resource.py $* $@ $(OLD_VERSION)

../owl/%_annotations.owl ../owl/%_sec.owl ../templates/class_template_%.csv ../templates/temp_ub_%_ASCTB_subset.csv ../templates/temp_cl_%_ASCTB_subset.csv ../templates/%_no-valid.csv ../logs/%/logs_dict.json: ../resources/ASCT-b_tables/%.json
	mkdir -p ../logs/$*
	python template_runner.py $* $< ../templates/class_template_$*.csv $(OLD_VERSION)

validation_reports_release_%: ../logs/%/logs_dict.json
	cp -a ../logs/$*/. ../docs/$*

../logs/%/README.md: ../logs/%/logs_dict.json validation_reports_release_%
	if [ $(OLD_VERSION) = False ]; then python readme_reports_generation.py --table $* --data $< --output $@ --mode "readme" && \
		cp $@ ../docs/$*/README.md && \
		rm $<; fi
.PRECIOUS: ../logs/%/README.md

../docs/%/graph.md: ../owl/ccf_%_classes.owl validation_reports_release_%
	if [ $(OLD_VERSION) = False ]; then cp -a ../graphs/ccf_$*_graph.png ../docs/$*/assets/. && \
		cp -a ../graphs/ccf_$*_graph.pdf ../docs/$*/assets/. && \
		python readme_reports_generation.py --table $* --output $@ --mode "graph"; fi
.PRECIOUS: ../docs/%/graph.md

../owl/ccf_%_classes_t.owl: ../templates/class_template_%.csv ../logs/%/README.md 
	$(ROBOT) $(CATALOG) template --add-prefix "CCFH: http://ccf_tools_helpers/class_helper.owl#" \
			--add-prefix "dc: http://purl.org/dc/elements/1.1/" \
			--add-prefix "skos: http://www.w3.org/2004/02/skos/core#" \
			--input helper.owl --template $< \
			--output $@

../owl/ub_%_ASCTB_subset.owl: ../templates/temp_ub_%_ASCTB_subset.csv ../docs/%/graph.md
	if [ $(OLD_VERSION) = False ]; then $(ROBOT) $(CATALOG) template --input helper.owl --template $< --output $@ && \
		rm $<; fi

../owl/cl_%_ASCTB_subset.owl: ../templates/temp_cl_%_ASCTB_subset.csv
	if [ $(OLD_VERSION) = False ]; then $(ROBOT) $(CATALOG) template --input helper.owl --template $< --output $@ && \
		rm $<; fi

../owl/%_no-valid.owl: ../templates/%_no-valid.csv
	if [ $(OLD_VERSION) = False ]; then $(ROBOT) $(CATALOG) template --input helper.owl --template $< --output $@ && \
		rm $<; fi

../owl/%_ASCTB_subset.json: ../owl/ub_%_ASCTB_subset.owl ../owl/cl_%_ASCTB_subset.owl
	if [ $(OLD_VERSION) = False ]; then $(ROBOT) merge $(patsubst %, -i %, $^) \
					 annotate --ontology-iri http://purl.org/ccf/latest/$*_ASCTB_subset.owl \
					 convert --format json -o $@; fi

.PRECIOUS: ../owl/%_ASCTB_subset.json

../owl/%_sec_reduced.owl:  ../owl/%_sec.owl
	if [ $(OLD_VERSION) = False ]; then $(ROBOT) $(CATALOG) merge --input helper.owl --input $< reduce --reasoner ELK -o ../owl/$*_sec_reduced.owl && \
		rm ../owl/$*_sec.owl; fi

../owl/ccf_%_classes.owl: ../owl/ccf_%_classes_t.owl ../owl/%_annotations.owl ../owl/%_no-valid.owl ../owl/%_sec_reduced.owl
	mkdir -p ../graphs
	if [ $(OLD_VERSION) = False ]; then $(ROBOT) $(CATALOG) merge --input helper.owl -i ../owl/ccf_$*_classes_t.owl -i ../owl/$*_annotations.owl -o $@ \
					 merge --input ../owl/$*_sec_reduced.owl -o ../owl/$*_extended.owl \
					 reduce --reasoner ELK \
					 merge -i ../owl/ccf_$*_classes_t.owl \
					 merge --input ../owl/$*_no-valid.owl \
					 annotate --ontology-iri http://purl.org/ccf/latest/ccf_$*_classes.owl \
					 convert --format json -o $*.json && \
		$(ROBOT) annotate --input ../owl/$*_sec_reduced.owl --ontology-iri http://purl.org/ccf/latest/$*_sec_reduced.owl convert -o $*_sec_reduced.json && \
		python graph_construct.py $*.json $*_sec_reduced.json $*_f.json "color" "green" && \
		og2dot.js -s ../style/ubergraph-style.json $*_f.json > $*.dot && \
		dot $*.dot -Tpng -Grankdir=LR > ../graphs/ccf_$*_graph.png && \
		dot $*.dot -Tpdf -Grankdir=LR > ../graphs/ccf_$*_graph.pdf && \
		rm $*.json && \
		rm $*_sec_reduced.json && \
		rm $*_f.json && \
		rm $*.dot; fi

../owl/last_official_ASCTB_release/ccf_%_classes.owl: ../owl/ccf_%_classes_t.owl ../owl/%_annotations.owl
	if [ $(OLD_VERSION) = True ]; then $(ROBOT) merge --input helper.owl -i ../owl/ccf_$*_classes_t.owl -i ../owl/$*_annotations.owl -o $@ \
					 annotate --ontology-iri http://purl.org/ccf/latest_official_ASCTB_release/ccf_$*_classes.owl \
					 convert --format json -o $*.json && \
		og2dot.js -s ../style/ubergraph-style.json $*.json > $*.dot &&\
		dot $*.dot -Tpng -Grankdir=LR > ../graphs/last_official_ASCTB_release/ccf_$*_graph.png && \
		dot $*.dot -Tpdf -Grankdir=LR > ../graphs/last_official_ASCTB_release/ccf_$*_graph.pdf && \
		rm $*.json && \
		rm $*.dot; fi

release_notes:
	python release_notes_generation.py
	rm tables_version.txt
	
../owl/CCF_AS_CT.owl: $(OWL_CLASS_FILES) $(OWL_CLASS_SEC_FILES) release_notes dashboard 3d-images_component
	if [ $(OLD_VERSION) = False ]; then $(ROBOT) $(CATALOG) merge $(patsubst %, -i %, $(OWL_CLASS_FILES)) \
					 merge $(patsubst %, -i %, $(OWL_CLASS_SEC_FILES)) \
					 reduce --reasoner ELK \
					 annotate --ontology-iri "http://purl.org/ccf/latest/CCF_AS_CT.owl" \
					 					--version-iri "http://purl.org/ccf/releases/$(VERSION)/CCF_AS_CT.owl" \
										--output $@ && \
		rm $(OWL_ANNOTATION_FILES) && \
		rm $(OWL_CLASS_SEC_FILES); fi

../owl/last_official_ASCTB_release/CCF_AS_CT.owl: $(OWL_CLASS_FILES_OLD)
	if [ $(OLD_VERSION) = True ]; then $(ROBOT) merge $(patsubst %, -i %, $^) \
						annotate --ontology-iri "http://purl.org/ccf/latest/CCF_AS_CT.owl" \
											--version-iri "http://purl.org/ccf/releases/$(VERSION)/CCF_AS_CT.owl" \
											--output $@ && \
		rm $(OWL_ANNOTATION_FILES_OLD); fi

../owl/UB_ASCTB_subset.owl: $(OWL_UB_SUBSET_FILES) $(JSON_CLASSES_SUBSET)
	if [ $(OLD_VERSION) = False ]; then $(ROBOT) $(CATALOG) merge $(patsubst %, -i %, $(OWL_UB_SUBSET_FILES)) --output $@ && \
		rm $(OWL_UB_SUBSET_FILES); fi

../owl/CL_ASCTB_subset.owl: $(OWL_CL_SUBSET_FILES)
	if [ $(OLD_VERSION) = False ]; then $(ROBOT) $(CATALOG) merge $(patsubst %, -i %, $^) --output $@ && \
		rm $(OWL_CL_SUBSET_FILES); fi

official_release:
	make ../owl/CCF_AS_CT.owl ../owl/UB_ASCTB_subset.owl ../owl/CL_ASCTB_subset.owl ../logs/ct_loc_markers/ct_loc_b_report.tsv -B
.PHONY: official_release

last_official_release:
	make ../owl/last_official_ASCTB_release/CCF_AS_CT.owl OLD_VERSION=True -B
.PHONY: last_official_release

../logs/ct_loc_markers/%_report.tsv: ../resources/ASCT-b_tables/%.json
	python cell_type_location.py --input $< --output $@ --mode generate
.PHONY: ../logs/ct_loc_markers/%_report.tsv

../logs/ct_loc_markers/ct_loc_b_report.tsv: ${CSV_CT_LOC_B}
	python cell_type_location.py --input $< --output $@ --mode merge
.PHONY: ../logs/ct_loc_markers/ct_loc_b_report.tsv

generate_dosdp_template: ../logs/ct_loc_markers/ct_loc_b_report.tsv
	python cell_type_location.py --input $< --output ../templates/ccf_compound.tsv --mode template

validation_reports_release: official_release
	cp -a ../logs/. ../docs

build-docker-v%:
	docker buildx use ccf-tools-dep-builder
	docker buildx build --platform linux/amd64,linux/arm64 -t anitacaron/ccf-tools-dep:v$* --push ../


### Import ODK standard
TODAY ?=                    $(shell date +%Y-%m-%d)
VERSION=                    $(TODAY)
ANNOTATE_ONTOLOGY_VERSION = 
ANNOTATE_CONVERT_FILE =     annotate --ontology-iri http://ccf_tools_helpers/class_helper/ro_import $(ANNOTATE_ONTOLOGY_VERSION) convert -f ofn --output $@.tmp.owl && mv $@.tmp.owl $@

mirror/ro.owl:
	curl -L http://purl.obolibrary.org/obo/ro.owl --create-dirs -o mirror/ro.owl --retry 4 --max-time 200 && $(ROBOT) convert -i mirror/ro.owl -o $@.tmp.owl && mv $@.tmp.owl $@
.PRECIOUS: mirror/ro.owl

imports/ro_import.owl: mirror/ro.owl imports/ro_terms.txt
	$(ROBOT) filter --input $< --term-file imports/ro_terms.txt --select "self annotations" \
		annotate --ontology-iri http://ccf_tools_helpers/class_helper/imports/ro_import.owl \
		annotate -V http://ccf_tools_helpers/class_helper/releases/imports/$(VERSION)/ro_import.owl --annotation owl:versionInfo $(VERSION) \
		convert -f ofn --output $@.tmp.owl && mv $@.tmp.owl $@
.PHONY: imports/ro_import.owl

dashboard:
	python dashboard_generation.py --output ../docs/dashboard.md
	# make build -f ../docs/Makefile

3d-images_component:
	python hra_wrapper.py
	$(ROBOT) convert -i ../owl/hra_uberon_3d_images.owl -f ofn -o ../owl/3d_images.tmp.owl
	mv ../owl/3d_images.tmp.owl ../owl/hra_uberon_3d_images.owl

FIRST_RELEASE=
LAST_RELEASE=
ID=

ONTOLOGIES=cl uberon

ontologies/latest_%.obo:
	mkdir -p ontologies/
	wget "http://purl.obolibrary.org/obo/$*.obo" -O $@

ontologies/uberon_%.obo:
	mkdir -p ontologies/
	wget "http://purl.obolibrary.org/obo/uberon/releases/$*/uberon-base.obo" -O $@

ontologies/cl_%.obo:
	mkdir -p ontologies/
	wget "http://purl.obolibrary.org/obo/cl/releases/$*/cl-base.obo" -O $@

stats/uberon_$(LAST_RELEASE)_diff.txt:
	$(eval ID := uberon)
	mkdir -p stats/
	$(MAKE) ontologies/$(ID)_$(FIRST_RELEASE).obo ontologies/$(ID)_$(LAST_RELEASE).obo
	runoak -i simpleobo:ontologies/$(ID)_$(FIRST_RELEASE).obo diff -X simpleobo:ontologies/$(ID)_$(LAST_RELEASE).obo --statistics -o $@.yaml
	robot diff --left ontologies/$(ID)_$(FIRST_RELEASE).obo --right ontologies/$(ID)_$(LAST_RELEASE).obo -o $@
.PRECIOUS: stats/uberon_$(LAST_RELEASE)_diff.txt

stats/cl_$(LAST_RELEASE)_diff.txt:
	$(eval ID := cl)
	mkdir -p stats/
	$(MAKE) ontologies/$(ID)_$(FIRST_RELEASE).obo ontologies/$(ID)_$(LAST_RELEASE).obo
	runoak -i simpleobo:ontologies/$(ID)_$(FIRST_RELEASE).obo diff -X simpleobo:ontologies/$(ID)_$(LAST_RELEASE).obo --statistics -o $@.yaml
	robot diff --left ontologies/$(ID)_$(FIRST_RELEASE).obo --right ontologies/$(ID)_$(LAST_RELEASE).obo -o $@
.PRECIOUS: stats/cl_$(LAST_RELEASE)_diff.txt

.PHONY: stats/cl_$(LAST_RELEASE)_diff_summary.txt
stats/cl_$(LAST_RELEASE)_diff_summary.txt: stats/cl_$(LAST_RELEASE)_diff.txt
	echo "Release $(LAST_RELEASE)" > $@
	echo "New Terms: " >> $@
	grep "+ Declaration.*CL" $< | wc -l >> $@
	echo "New or updated definitions: " >> $@
	grep -E "[+] AnnotationAssertion.*IAO_0000115" $< | wc -l >> $@
	echo "New or updated synonyms: " >> $@
	grep -E "[+] AnnotationAssertion.*Synonym" $< | wc -l >> $@
	echo "New or updated part of relationship: " >> $@
	grep -E "[+] SubClassOf.*CL.*BFO_0000050" $< | wc -l >> $@
	echo "New or updated has part relationship: " >> $@
	grep -E "[+] SubClassOf.*CL.*BFO_0000051" $< | wc -l >> $@
	echo "New or updated subclassof relationship: " >> $@
	grep -E "[+] SubClassOf" $< | grep -E -v "BFO|RO" | wc -l >> $@

.PHONY: stats/uberon_$(LAST_RELEASE)_diff_summary.txt
stats/uberon_$(LAST_RELEASE)_diff_summary.txt: stats/uberon_$(LAST_RELEASE)_diff.txt
	echo "Release $(LAST_RELEASE)" > $@
	echo "New Terms: " >> $@
	grep "+ Declaration.*UBERON" $< | wc -l >> $@
	echo "New or updated definitions: " >> $@
	grep -E "[+] AnnotationAssertion.*IAO_0000115" $< | wc -l >> $@
	echo "New or updated synonyms: " >> $@
	grep -E "[+] AnnotationAssertion.*Synonym" $< | wc -l >> $@
	echo "New or updated 'part of' relationship: " >> $@
	grep -E "[+] SubClassOf.*UBERON.*BFO_0000050.*UBERON" $< | wc -l >> $@
	echo "New or updated 'has part' relationship: " >> $@
	grep -E "[+] SubClassOf.*UBERON.*BFO_0000051.*UBERON" $< | wc -l >> $@
	echo "New or updated 'connecting branch of' relationship: " >> $@
	grep -E "[+] SubClassOf.*UBERON.*RO_0002252.*UBERON" $< | wc -l >> $@
	echo "New or updated 'connected to' relationship: " >> $@
	grep -E "[+] SubClassOf.*UBERON.*RO_0002170" $< | wc -l >> $@
	echo "New or updated subclassof relationship:" >> $@
	grep -E "[+] SubClassOf.*UBERON.*UBERON" $< | grep -E -v "BFO|RO_" | wc -l >> $@
	echo "New or updated surrounds relationship:" >> $@
	grep -E "[+] SubClassOf.*UBERON.*RO_0002221.*UBERON" $< | wc -l >> $@
