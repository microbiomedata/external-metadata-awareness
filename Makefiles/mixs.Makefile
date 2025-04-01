RUN=poetry run
WGET=wget

# preferable to use a tagged release, but theres good stuff in this commit that hasn't been released yet
MIXS_YAML_URL=https://raw.githubusercontent.com/GenomicsStandardsConsortium/mixs/b0b1e03b705cb432d08914c686ea820985b9cb20/src/mixs/schema/mixs.yaml

downloads/mixs.yaml:
	wget -O $@ $(MIXS_YAML_URL)

local/mixs-slots-enums.json: downloads/mixs.yaml
	yq eval '{"slots": .slots, "enums": .enums}' -o=json $< | cat > $@

local/mixs-slots-enums-no-MixsCompliantData-domain.json: local/mixs-slots-enums.json
	yq e '.slots |= (del(.[] | select(.domain == "MixsCompliantData"))) | del(.[].keywords)' $< | cat > $@

local/mixs-slots-sex-gender-analysis-prompt.txt: prompt-templates/mixs-slots-sex-gender-analysis-prompt.yaml \
local/mixs-slots-enums-no-MixsCompliantData-domain.json
	$(RUN) build-prompt-from-template \
		--spec-file-path $(word 1,$^) \
		--output-file-path $@

local/mixs-slots-sex-gender-analysis-response.txt: local/mixs-slots-sex-gender-analysis-prompt.txt
	# cborg/claude-opus
	cat $(word 1,$^) | $(RUN) llm prompt --model claude-3.5-sonnet -o temperature 0.01 | tee $@

# getting fragments of MIxS because the whole thing is too large to feed into an LLM
local/mixs-extensions-with-slots.json: downloads/mixs.yaml
	yq -o=json e '.classes | with_entries(select(.value.is_a == "Extension") | .value |= del(.slot_usage))' $< | cat > $@

local/mixs-extensions.json: downloads/mixs.yaml
	yq -o=json e '.classes | with_entries(select(.value.is_a == "Extension") | .value |= del(.slots, .slot_usage))' $< | cat > $@

local/mixs-env-triad.json: downloads/mixs.yaml
	yq -o=json e '{"slots": {"env_broad_scale": .slots.env_broad_scale, "env_local_scale": .slots.env_local_scale, "env_medium": .slots.env_medium}}' $< | cat > $@
