# AI Guidelines Adherence Implementation Plan

**Created**: 2025-09-26 11:17:00 UTC  
**Last Updated**: 2025-09-26 11:55:00 UTC  
**Task ID**: AI Guidelines Adherence Implementation  
**Based on Analysis**: ai_guidelines_adherence_analysis_20250926.md  
**Integrated with**: tct_guidelines_integration_analysis_20250926.md

## Executive Summary

This implementation plan provides detailed interventions to address AI agent non-compliance with A2G guidelines. Based on comprehensive root cause analysis, user requirements, and TCT guidelines integration analysis, the plan focuses on enhancing the A2G framework itself while implementing strategic enhancements to repository guidelines using the recommended enhanced integration approach.

**Primary Goal**: Achieve 100% A2G guideline compliance for AI agents operating in TCT repository through A2G framework enhancements and targeted repository guidelines integration.

**Key Constraint**: Minimize repository guidelines changes since A2G framework exists to prevent instruction repetition across projects.

**Integration Strategy**: Implements enhanced integration approach (Option A) from TCT guidelines integration analysis, preserving existing guidelines structure while adding specific AI agent compliance requirements.

## Implementation Strategy Overview

### Phase 1: A2G Framework Enhancement (Week 1-2)
- Add Task Verb Interpretation to A2G general guidelines
- Add File Creation Protocol to A2G general guidelines
- Add Workflow Mode Compliance to A2G general guidelines
- Add Violation Consequences to A2G general guidelines
- Enhanced repository guidelines integration (Option A from integration analysis)
- Create A2G Consumer Project validation and patching script
- Update A2G template files for consumer projects

### Phase 2: System Integration (Week 3-4)
- Automated compliance checking tools
- Pre-task validation integration
- Real-time guideline enforcement

### Phase 3: Long-term Optimization (Week 5-8)
- Performance monitoring framework
- Advanced training protocols
- Continuous improvement system

## Detailed Implementation Plan

### 1. A2G Framework Enhancement

#### 1.1 Update A2G General Guidelines

**Intervention**: Add critical AI agent compliance sections to A2G framework

**Target File**: `.junie/ai_agent_guidelines/guidelines/guidelines.a2g_general.md`

**Implementation**: Add the following sections to A2G general guidelines:

**Section A: Task Verb Interpretation**
```markdown
## A2G Task Verb Interpretation Protocol

AI agents must interpret task verbs precisely:

### Critical Verb Distinctions:
- **"Propose a plan"** = Create plan document in `.junie/ai_artifact/plans/` ONLY
- **"Implement a plan"** = Execute approved plan (requires prior approval in supervised mode)
- **"Analyze"** = Create analysis document in `.junie/ai_artifact/reports/` ONLY  
- **"Write"** = Follow A2G file placement decision tree based on content type
- **"Create"** = Follow A2G file placement decision tree based on content type

### Compliance Rule:
Never start implementation when asked to "propose" - this violates the planning phase requirements.
```

**Section B: Enhanced File Creation Protocol**
```markdown
## A2G Mandatory File Creation Protocol

**BEFORE creating ANY file, AI agents must**:
1. Consult A2G file placement decision tree
2. Determine file classification (temporary vs permanent)
3. Verify workflow mode permissions from `.junie/a2g_config.yml`
4. Apply correct naming conventions per A2G standards

### Pre-Creation Validation Questions:
- What is the intended lifespan of this file?
- Is this a plan, report, log, or implementation file?
- What does the A2G file placement decision tree specify?
- Am I authorized in current workflow mode?
```

**Section C: Workflow Mode Compliance**
```markdown
## A2G Workflow Mode Compliance

AI agents must check workflow mode before any action:

### Supervised Mode Requirements:
- Request approval before implementation tasks
- Can create plans and reports without approval
- Must follow all A2G artifact management rules

### Autonomous Mode Requirements:
- Can proceed with implementation after approved planning
- Must still follow all A2G guidelines and file placement rules
```

**Section D: Violation Consequences**
```markdown
## A2G Compliance Violation Consequences

Non-compliance with A2G protocols results in:
1. **Immediate task rejection** and restart requirement
2. **Mandatory A2G guideline review** before proceeding
3. **AI operator escalation** for persistent violations
4. **Workflow mode restriction** for repeated failures
```

#### 1.2 Enhanced Repository Guidelines Integration

**Intervention**: Implement enhanced integration approach based on TCT guidelines integration analysis

**Target File**: `.junie/guidelines.md`

**Analysis Findings**: The existing "Repository Guidelines Instructions" and "Prime directive" sections are useful but need enhancement with specific AI agent requirements. Integration should be additive and backward compatible.

**Implementation Strategy**: Enhanced Integration (Option A from analysis)

**Current State**:
```markdown
## Repository Guidelines Instructions

1. First, review and learn _A2G Framework Guidelines_ specified in
  `.junie/ai_agent_guidelines/guidelines.a2g_framework.md`.
2. Then review the remaining repository guidelines below.

## Prime directive

Always comply with _A2G Framework Guidelines_, _Repository Guidelines_ and _AI operator_ instructions.
```

**Enhanced State** (add the following):

1. **Enhance Repository Guidelines Instructions** - Add line 3:
```markdown
## Repository Guidelines Instructions

1. First, review and learn _A2G Framework Guidelines_ specified in
  `.junie/ai_agent_guidelines/guidelines.a2g_framework.md`.
2. Then review the remaining repository guidelines below.
3. **AI agents must follow the mandatory compliance requirements specified below.**
```

2. **Keep Prime directive unchanged** (already well-structured)

3. **Add new AI Agent Compliance Requirements section**:
```markdown
## AI Agent Compliance Requirements

All AI agents must:
1. **Always** review A2G guidelines before starting any task
2. **Always** follow A2G file placement decision tree  
3. **Always** check workflow mode in `.junie/a2g_config.yml`
4. **Always** apply A2G task verb interpretation protocols

See A2G general guidelines for complete procedures and requirements.
```

**Benefits of Enhanced Integration**:
- ✅ Maintains A2G framework principle (minimal repository additions)
- ✅ Leverages existing well-structured sections
- ✅ Backward compatible (no breaking changes)
- ✅ Adds only 6 lines of specific requirements
- ✅ Addresses root causes of non-compliance

**Success Criteria**:
- Existing guidelines sections preserved and enhanced
- Clear mandatory compliance requirements added
- No duplication of A2G configuration content
- Integration follows analysis recommendations

#### 1.3 A2G Consumer Project Validation and Patching Script

**Intervention**: Create comprehensive validation and patching script for A2G-consumer-project level guidelines sanity checks

**Target Location**: `.junie/ai_agent_guidelines/tools/validate_and_patch_a2g_consumer_project.py`

**Purpose**: Perform automated validation and correction of A2G-consumer-project guidelines compliance, ensuring all required A2G entries are present and correctly formatted in both `.junie/a2g_config.yml` and `.junie/guidelines.md` files.

**Implementation Requirements**:

The script must execute the following steps:

1. **Read A2G-consumer-project configuration files**:
   - Load `.junie/a2g_config.yml` 
   - Load `.junie/guidelines.md`

2. **Validate required A2G entries in `.junie/guidelines.md`**:
   - Check for `# Repository Guidelines` section
   - Check for `## Repository Description` section  
   - Check for `## Repository Guidelines Instructions`, `## Prime directive` and `## AI Agent Compliance Requirements` sections with exact content:
   ```markdown
   ## Repository Guidelines Instructions
   
   1. First, review and learn _A2G Framework Guidelines_ specified in
     `.junie/ai_agent_guidelines/guidelines.a2g_framework.md`.
   2. Then review the remaining repository guidelines below.
   3. **AI agents must follow the mandatory compliance requirements specified below.**
   
   ## Prime directive
     
   Always comply with _A2G Framework Guidelines_, _Repository Guidelines_ and _AI operator_ instructions.

   ## AI Agent Compliance Requirements
   
   All AI agents must:
   1. **Always** review A2G guidelines before starting any task
   2. **Always** follow A2G file placement decision tree  
   3. **Always** check workflow mode in `.junie/a2g_config.yml`
   4. **Always** apply A2G task verb interpretation protocols
   
   See A2G general guidelines for complete procedures and requirements.
   ```
   - Check for `## Repository Organization` section
   - Check for `## Repository Terminology` section
   - Check for `## Repository Specific Additional Guidelines` section

3. **Validate required A2G entries in `.junie/a2g_config.yml`**:
   - Compare with template at `.junie/ai_agent_guidelines/template/junie_template/a2g_config.yml`
   - Ensure all keys from template are present in consumer project config
   - Verify each key has a non-empty entry

4. **Add missing entries or update non-compliant entries**:
   - Automatically add missing sections to guidelines.md
   - Update sections that don't comply with required format
   - Add missing keys to a2g_config.yml with appropriate default values

5. **Create backup copies**:
   - Create `*.old` postfix backup before modifying original files
   - Preserve original file permissions and timestamps where possible

6. **Warn user of changes**:
   - Log all modifications made to console and log file
   - Provide detailed diff of changes for review
   - Exit with appropriate status codes

**Script Architecture**:

```python
#!/usr/bin/env python3
"""
A2G Consumer Project Validation and Patching Script

This script performs automated validation and correction of A2G-consumer-project 
guidelines compliance, ensuring all required A2G entries are present and correctly 
formatted in both configuration and guidelines files.

Location: .junie/ai_agent_guidelines/tools/validate_and_patch_a2g_consumer_project.py
"""

import os
import sys
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of validation check"""
    is_valid: bool
    issues: List[str]
    fixes_applied: List[str]

class A2GConsumerProjectValidator:
    """Validates and patches A2G consumer project compliance"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.a2g_config_path = repo_root / ".junie" / "a2g_config.yml"
        self.guidelines_path = repo_root / ".junie" / "guidelines.md"
        self.template_config_path = repo_root / ".junie" / "ai_agent_guidelines" / "template" / "junie_template" / "a2g_config.yml"
        
        # Required sections and their content
        self.required_guidelines_sections = {
            "# Repository Guidelines": True,
            "## Repository Description": True,
            "## Repository Guidelines Instructions": self._get_required_instructions_content(),
            "## Prime directive": self._get_required_prime_directive_content(),
            "## AI Agent Compliance Requirements": self._get_required_compliance_content(),
            "## Repository Organization": True,
            "## Repository Terminology": True,
            "## Repository Specific Additional Guidelines": True
        }
    
    def _get_required_instructions_content(self) -> str:
        return """## Repository Guidelines Instructions

1. First, review and learn _A2G Framework Guidelines_ specified in
  `.junie/ai_agent_guidelines/guidelines.a2g_framework.md`.
2. Then review the remaining repository guidelines below.
3. **AI agents must follow the mandatory compliance requirements specified below.**"""
    
    def _get_required_prime_directive_content(self) -> str:
        return """## Prime directive
  
Always comply with _A2G Framework Guidelines_, _Repository Guidelines_ and _AI operator_ instructions."""
    
    def _get_required_compliance_content(self) -> str:
        return """## AI Agent Compliance Requirements

All AI agents must:
1. **Always** review A2G guidelines before starting any task
2. **Always** follow A2G file placement decision tree  
3. **Always** check workflow mode in `.junie/a2g_config.yml`
4. **Always** apply A2G task verb interpretation protocols

See A2G general guidelines for complete procedures and requirements."""
    
    def validate_a2g_config(self) -> ValidationResult:
        """Validate A2G config against template"""
        # Implementation details for config validation
        pass
    
    def validate_guidelines(self) -> ValidationResult:
        """Validate guidelines file for required sections"""
        # Implementation details for guidelines validation
        pass
    
    def create_backup(self, file_path: Path) -> Path:
        """Create backup file with .old suffix"""
        backup_path = file_path.with_suffix(file_path.suffix + '.old')
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def patch_files(self, validation_results: List[ValidationResult]) -> None:
        """Apply patches to fix validation issues"""
        # Implementation details for patching
        pass
    
    def run_validation(self) -> Dict[str, ValidationResult]:
        """Run complete validation and patching process"""
        results = {}
        
        # Validate config
        results['config'] = self.validate_a2g_config()
        
        # Validate guidelines  
        results['guidelines'] = self.validate_guidelines()
        
        # Apply patches if needed
        if not all(result.is_valid for result in results.values()):
            self.patch_files(list(results.values()))
        
        return results

def main():
    """Main entry point"""
    repo_root = Path.cwd()
    validator = A2GConsumerProjectValidator(repo_root)
    
    try:
        results = validator.run_validation()
        
        # Report results
        all_valid = all(result.is_valid for result in results.values())
        
        if all_valid:
            print("✅ A2G Consumer Project validation passed!")
            sys.exit(0)
        else:
            print("⚠️  A2G Consumer Project validation found issues - patches applied")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
```

**Success Criteria**:
- Successfully validates both configuration and guidelines files
- Automatically patches missing or incorrect entries
- Creates proper backups before modifications
- Provides clear user feedback on all changes
- Handles edge cases and error conditions gracefully

#### 1.5 Update A2G Template Files

**Intervention**: Update template files in `.junie/ai_agent_guidelines/template/junie_template` according to plan requirements

**Target Files**: 
- `.junie/ai_agent_guidelines/template/junie_template/guidelines.md`
- `.junie/ai_agent_guidelines/template/junie_template/a2g_config.yml` (if needed)

**Purpose**: Ensure A2G template files reflect the enhanced integration approach and include all mandatory AI agent compliance requirements for new A2G-consumer-projects.

**Implementation Requirements**:

**Template Guidelines Update**:
The template `guidelines.md` must include the enhanced integration structure:

```markdown
# Repository Guidelines

[//]: # (TODO_REPO_NAME guidelines and instructions)

## Repository Description

[//]: # (TODO: Add repository description)

## Repository Guidelines Instructions

1. First, review and learn _A2G Framework Guidelines_ specified in
  `.junie/ai_agent_guidelines/guidelines.a2g_framework.md`.
2. Then review the remaining repository guidelines below.
3. **AI agents must follow the mandatory compliance requirements specified below.**

## Prime directive

Always comply with _A2G Framework Guidelines_, _Repository Guidelines_ and _AI operator_ instructions.

## AI Agent Compliance Requirements

All AI agents must:
1. **Always** review A2G guidelines before starting any task
2. **Always** follow A2G file placement decision tree  
3. **Always** check workflow mode in `.junie/a2g_config.yml`
4. **Always** apply A2G task verb interpretation protocols

See A2G general guidelines for complete procedures and requirements.

## Repository Organization

- `.dockerized_norlab` contains DNA configuration files.
- `.junie/` contains AI agent related files.
- `.junie/ai_agent_guidelines` contains _AI Agent Guidelines (A2G)_ with entrypoint at
  `.junie/ai_agent_guidelines/README.md`.
- `src/` contains repository source code.
- `tests/` contains tests files.
- `artifact/` contains runtime produced data such as experimental log, plot and trained model.
- `data/` contains input data such as _test data_, _demo data_ or _experimental data_.
- `utilities/` contains external libraries.

[//]: # (TODO: add missing directory)

## Repository Terminology

- **DNA**: Dockerized-NorLab project application.

[//]: # (TODO: add new terminology to limit AI agent confusion. )

## Repository Specific Additional Guidelines

[//]: # (TODO: add repository specific additionale guidelines if any.)

Proceed with _AI operator_ instructions

```

**Implementation Steps**:
1. Review current template guidelines structure
2. Update template to include enhanced AI Agent Compliance Requirements section
3. Ensure compatibility with validation script requirements
4. Verify template matches the exact format expected by validation script
5. Update any related template documentation or examples

**Success Criteria**:
- Template guidelines include all required sections for validation script
- New A2G-consumer-projects created from template will pass validation automatically
- Template structure matches enhanced integration approach (Option A)
- Backward compatibility maintained for existing projects

#### 1.4 Create Pre-Task Validation Script

**Intervention**: Automated pre-task checklist validation

**Implementation**: Create validation script at `.junie/ai_artifact/tmp/temp_pretask_validator_20250926.py`:

```python
"""
TEMPORARY VALIDATION TOOL - Expected removal: After integration into A2G framework

This script validates AI agent pre-task checklist compliance and is intended for 
temporary use during implementation phase.
Created for task: AI Guidelines Adherence Implementation
Removal condition: After successful integration of automated validation
"""

import os
import yaml
from pathlib import Path

class A2GPreTaskValidator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.a2g_config_path = repo_root / ".junie" / "a2g_config.yml"
        self.guidelines_path = repo_root / ".junie" / "guidelines.md"
        
    def validate_a2g_config_access(self) -> dict:
        """Validate AI agent can access and read A2G configuration"""
        try:
            with open(self.a2g_config_path, 'r') as f:
                config = yaml.safe_load(f)
            return {
                'status': 'PASS',
                'workflow_mode': config.get('A2G', {}).get('workflow', 'unknown'),
                'specialized_guidelines': config.get('specialized_guidelines', [])
            }
        except Exception as e:
            return {'status': 'FAIL', 'error': str(e)}
    
    def validate_guidelines_access(self) -> dict:
        """Validate AI agent can access repository guidelines"""
        try:
            with open(self.guidelines_path, 'r') as f:
                content = f.read()
            has_ai_protocol = "AI Agent Task Execution Protocol" in content
            return {
                'status': 'PASS',
                'has_ai_protocol': has_ai_protocol,
                'file_size': len(content)
            }
        except Exception as e:
            return {'status': 'FAIL', 'error': str(e)}
    
    def validate_artifact_structure(self) -> dict:
        """Validate .junie/ai_artifact directory structure exists"""
        artifact_path = self.repo_root / ".junie" / "ai_artifact"
        required_dirs = ['plans', 'reports', 'logs', 'tmp']
        
        results = {}
        for dir_name in required_dirs:
            dir_path = artifact_path / dir_name
            results[dir_name] = dir_path.exists()
            
        return {
            'status': 'PASS' if all(results.values()) else 'FAIL',
            'directories': results
        }
    
    def run_full_validation(self) -> dict:
        """Run complete pre-task validation"""
        return {
            'a2g_config': self.validate_a2g_config_access(),
            'guidelines': self.validate_guidelines_access(),
            'artifact_structure': self.validate_artifact_structure()
        }

if __name__ == "__main__":
    repo_root = Path.cwd()
    validator = A2GPreTaskValidator(repo_root)
    results = validator.run_full_validation()
    
    print("=== A2G Pre-Task Validation Results ===")
    for category, result in results.items():
        status = result.get('status', 'UNKNOWN')
        print(f"\n{category.upper()}: {status}")
        if status == 'FAIL':
            print(f"  Error: {result.get('error', 'Unknown error')}")
        else:
            for key, value in result.items():
                if key != 'status':
                    print(f"  {key}: {value}")
```

**Success Criteria**:
- Script successfully validates A2G access
- Identifies configuration issues
- Provides actionable feedback

### 2. File Placement Enforcement System

#### 2.1 Create File Placement Decision Engine

**Intervention**: Automated file placement validation based on A2G decision tree

**Implementation**: Create `.junie/ai_artifact/tmp/temp_file_placement_validator_20250926.py`:

```python
"""
TEMPORARY VALIDATION TOOL - Expected removal: After A2G framework integration

Validates file placement decisions according to A2G guidelines decision tree.
Created for task: AI Guidelines Adherence Implementation
"""

from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional

class FileType(Enum):
    PLAN = "plan"
    REPORT = "report"
    LOG = "log"
    IMPLEMENTATION = "implementation"
    TEMPORARY = "temporary"

class A2GFilePlacementValidator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.placement_rules = {
            FileType.PLAN: ".junie/ai_artifact/plans/",
            FileType.REPORT: ".junie/ai_artifact/reports/",
            FileType.LOG: ".junie/ai_artifact/logs/",
            FileType.TEMPORARY: ".junie/ai_artifact/tmp/",
            FileType.IMPLEMENTATION: "src/"  # or appropriate project directory
        }
    
    def classify_file_intent(self, file_purpose: str, is_temporary: bool = False) -> FileType:
        """Classify file based on purpose following A2G decision tree"""
        
        # Step 1: Is this temporary?
        if is_temporary or any(keyword in file_purpose.lower() for keyword in 
                             ['temp', 'debug', 'validation', 'oneshot', 'poc']):
            return FileType.TEMPORARY
        
        # Step 2: Is this a report/analysis?
        if any(keyword in file_purpose.lower() for keyword in 
               ['report', 'analysis', 'assessment', 'summary']):
            return FileType.REPORT
        
        # Step 3: Is this a plan?
        if 'plan' in file_purpose.lower():
            return FileType.PLAN
        
        # Step 4: Is this a log?
        if 'log' in file_purpose.lower():
            return FileType.LOG
        
        # Step 5: Implementation-related?
        if any(keyword in file_purpose.lower() for keyword in 
               ['source', 'code', 'test', 'config', 'implementation']):
            return FileType.IMPLEMENTATION
        
        # Default to temporary if unclear
        return FileType.TEMPORARY
    
    def get_correct_path(self, filename: str, file_type: FileType) -> str:
        """Get correct path for file based on type"""
        return self.placement_rules[file_type] + filename
    
    def validate_file_placement(self, intended_path: str, file_purpose: str, 
                              is_temporary: bool = False) -> Dict:
        """Validate if intended file placement follows A2G guidelines"""
        
        file_type = self.classify_file_intent(file_purpose, is_temporary)
        correct_path = self.get_correct_path(Path(intended_path).name, file_type)
        
        is_correct = intended_path == correct_path or intended_path.endswith(correct_path)
        
        return {
            'is_correct': is_correct,
            'file_type': file_type.value,
            'intended_path': intended_path,
            'correct_path': correct_path,
            'recommendation': f"Move to {correct_path}" if not is_correct else "Placement is correct"
        }

def validate_common_scenarios():
    """Test common file placement scenarios"""
    repo_root = Path.cwd()
    validator = A2GFilePlacementValidator(repo_root)
    
    test_cases = [
        ("my_plan.md", "implementation plan for feature X", False),
        ("analysis_report.md", "analysis of system performance", False),
        ("temp_validation.py", "temporary validation script", True),
        ("debug_tool.py", "debugging utility for development", True),
        ("feature_implementation.py", "source code for new feature", False),
    ]
    
    print("=== File Placement Validation Results ===")
    for filename, purpose, is_temp in test_cases:
        result = validator.validate_file_placement(filename, purpose, is_temp)
        status = "✅" if result['is_correct'] else "❌"
        print(f"\n{status} File: {filename}")
        print(f"   Purpose: {purpose}")
        print(f"   Type: {result['file_type']}")
        print(f"   Recommendation: {result['recommendation']}")

if __name__ == "__main__":
    validate_common_scenarios()
```

**Success Criteria**:
- Correctly classifies file types according to A2G decision tree
- Provides accurate placement recommendations
- Handles edge cases and ambiguous scenarios

### 3. Workflow Mode Enforcement

#### 3.1 Create Workflow Mode Monitor

**Intervention**: Real-time workflow mode compliance checking

**Implementation**: Create `.junie/ai_artifact/tmp/temp_workflow_monitor_20250926.py`:

```python
"""
TEMPORARY MONITORING TOOL - Expected removal: After A2G framework integration

Monitors workflow mode compliance during AI agent task execution.
Created for task: AI Guidelines Adherence Implementation
"""

import yaml
from pathlib import Path
from enum import Enum
from typing import Dict, List

class WorkflowMode(Enum):
    SUPERVISED = "supervised"
    AUTONOMOUS = "autonomous"

class TaskType(Enum):
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    ANALYSIS = "analysis"
    REPORTING = "reporting"

class WorkflowModeMonitor:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.config_path = repo_root / ".junie" / "a2g_config.yml"
        
    def get_current_workflow_mode(self) -> WorkflowMode:
        """Read current workflow mode from A2G config"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            mode_str = config.get('A2G', {}).get('workflow', 'supervised')
            return WorkflowMode(mode_str)
        except Exception:
            return WorkflowMode.SUPERVISED  # Default to most restrictive
    
    def classify_task(self, task_description: str) -> TaskType:
        """Classify task type based on description"""
        task_lower = task_description.lower()
        
        if any(keyword in task_lower for keyword in ['propose', 'plan', 'design']):
            return TaskType.PLANNING
        elif any(keyword in task_lower for keyword in ['implement', 'code', 'create', 'build']):
            return TaskType.IMPLEMENTATION
        elif any(keyword in task_lower for keyword in ['analyze', 'investigate', 'study']):
            return TaskType.ANALYSIS
        elif any(keyword in task_lower for keyword in ['report', 'document', 'summarize']):
            return TaskType.REPORTING
        else:
            return TaskType.PLANNING  # Default to planning for safety
    
    def validate_task_permission(self, task_description: str) -> Dict:
        """Validate if task is allowed under current workflow mode"""
        current_mode = self.get_current_workflow_mode()
        task_type = self.classify_task(task_description)
        
        # Define permissions for each mode
        permissions = {
            WorkflowMode.SUPERVISED: {
                TaskType.PLANNING: True,
                TaskType.ANALYSIS: True,
                TaskType.REPORTING: True,
                TaskType.IMPLEMENTATION: False  # Requires approval
            },
            WorkflowMode.AUTONOMOUS: {
                TaskType.PLANNING: True,
                TaskType.ANALYSIS: True,
                TaskType.REPORTING: True,
                TaskType.IMPLEMENTATION: True
            }
        }
        
        is_allowed = permissions[current_mode][task_type]
        
        result = {
            'is_allowed': is_allowed,
            'workflow_mode': current_mode.value,
            'task_type': task_type.value,
            'task_description': task_description
        }
        
        if not is_allowed:
            result['action_required'] = "Request approval from AI operator before proceeding"
            result['escalation_needed'] = True
        else:
            result['action_required'] = "Proceed following A2G guidelines"
            result['escalation_needed'] = False
            
        return result

def test_workflow_scenarios():
    """Test common workflow scenarios"""
    repo_root = Path.cwd()
    monitor = WorkflowModeMonitor(repo_root)
    
    test_tasks = [
        "Propose a plan for implementing new feature",
        "Implement the approved authentication system", 
        "Analyze the current codebase structure",
        "Create a performance report",
        "Build the new user interface components"
    ]
    
    print("=== Workflow Mode Compliance Check ===")
    print(f"Current mode: {monitor.get_current_workflow_mode().value}")
    
    for task in test_tasks:
        result = monitor.validate_task_permission(task)
        status = "✅" if result['is_allowed'] else "❌"
        print(f"\n{status} Task: {task}")
        print(f"   Type: {result['task_type']}")
        print(f"   Action: {result['action_required']}")
        if result['escalation_needed']:
            print(f"   ⚠️  Escalation required!")

if __name__ == "__main__":
    test_workflow_scenarios()
```

**Success Criteria**:
- Correctly identifies current workflow mode
- Accurately classifies task types
- Provides appropriate permission validation

### 4. Integration with Repository Guidelines

#### 4.1 Guidelines Update Implementation

**Intervention**: Add comprehensive AI agent protocol to repository guidelines

**Current `.junie/guidelines.md` Status**: Lacks AI agent specific instructions  
**Required Action**: Append new section with mandatory protocols

**Implementation Steps**:

1. **Backup current guidelines**:
   ```bash
   cp .junie/guidelines.md .junie/guidelines.md.backup
   ```

2. **Append new AI Agent Protocol section** (detailed content provided in section 1.1)

3. **Validate integration**:
   - Ensure no conflicts with existing guidelines
   - Verify A2G hierarchy is maintained
   - Test guideline accessibility

**Success Criteria**:
- AI agents consistently reference new protocols
- No conflicts with existing repository guidelines
- 100% compliance with new mandatory steps

### 5. Performance Measurement Framework

#### 5.1 Compliance Metrics Dashboard

**Intervention**: Create comprehensive monitoring system

**Implementation**: Create `.junie/ai_artifact/tmp/temp_compliance_dashboard_20250926.py`:

```python
"""
TEMPORARY MONITORING DASHBOARD - Expected removal: After A2G framework integration

Tracks AI agent compliance with A2G guidelines and generates performance reports.
Created for task: AI Guidelines Adherence Implementation
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class ComplianceEvent:
    timestamp: str
    agent_session: str
    task_type: str
    compliance_area: str  # file_placement, task_interpretation, workflow_mode
    status: str  # PASS, FAIL, WARNING
    details: str
    corrective_action: Optional[str] = None

class ComplianceTracker:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.log_file = repo_root / ".junie" / "ai_artifact" / "logs" / "compliance_log.json"
        self.events: List[ComplianceEvent] = []
        self.load_existing_events()
    
    def load_existing_events(self):
        """Load existing compliance events from log file"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                self.events = [ComplianceEvent(**event) for event in data]
            except Exception as e:
                print(f"Error loading compliance log: {e}")
    
    def log_event(self, event: ComplianceEvent):
        """Log a compliance event"""
        self.events.append(event)
        self.save_events()
    
    def save_events(self):
        """Save events to log file"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump([asdict(event) for event in self.events], f, indent=2)
    
    def generate_compliance_report(self) -> Dict:
        """Generate comprehensive compliance report"""
        if not self.events:
            return {"status": "No compliance events recorded"}
        
        total_events = len(self.events)
        
        # Status distribution
        status_counts = {}
        for event in self.events:
            status_counts[event.status] = status_counts.get(event.status, 0) + 1
        
        # Compliance area breakdown
        area_stats = {}
        for event in self.events:
            area = event.compliance_area
            if area not in area_stats:
                area_stats[area] = {"PASS": 0, "FAIL": 0, "WARNING": 0}
            area_stats[area][event.status] = area_stats[area].get(event.status, 0) + 1
        
        # Calculate success rates
        success_rates = {}
        for area, stats in area_stats.items():
            total = sum(stats.values())
            pass_rate = (stats.get("PASS", 0) / total) * 100 if total > 0 else 0
            success_rates[area] = round(pass_rate, 2)
        
        # Recent failures
        recent_failures = [
            event for event in self.events[-20:]  # Last 20 events
            if event.status == "FAIL"
        ]
        
        return {
            "summary": {
                "total_events": total_events,
                "status_distribution": status_counts,
                "overall_success_rate": round(
                    (status_counts.get("PASS", 0) / total_events) * 100, 2
                ) if total_events > 0 else 0
            },
            "area_performance": {
                "success_rates": success_rates,
                "detailed_stats": area_stats
            },
            "recent_issues": [
                {
                    "timestamp": event.timestamp,
                    "area": event.compliance_area,
                    "details": event.details,
                    "corrective_action": event.corrective_action
                }
                for event in recent_failures
            ]
        }

# Example usage and test data generation
def generate_sample_data():
    """Generate sample compliance data for testing"""
    repo_root = Path.cwd()
    tracker = ComplianceTracker(repo_root)
    
    # Sample events
    sample_events = [
        ComplianceEvent(
            timestamp=datetime.now().isoformat(),
            agent_session="session_001",
            task_type="planning",
            compliance_area="file_placement",
            status="PASS",
            details="Plan correctly placed in .junie/ai_artifact/plans/"
        ),
        ComplianceEvent(
            timestamp=datetime.now().isoformat(),
            agent_session="session_002", 
            task_type="implementation",
            compliance_area="workflow_mode",
            status="FAIL",
            details="Implementation attempted in supervised mode without approval",
            corrective_action="Escalated to AI operator for approval"
        )
    ]
    
    for event in sample_events:
        tracker.log_event(event)
    
    report = tracker.generate_compliance_report()
    print("=== Compliance Dashboard ===")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    generate_sample_data()
```

**Success Criteria**:
- Tracks all compliance events accurately
- Generates actionable performance reports
- Identifies patterns in non-compliance

## Implementation Timeline

### Week 1: Foundation Setup
- **Day 1-2**: Update `.junie/guidelines.md` with AI Agent Protocol
- **Day 3-4**: Create and test pre-task validation scripts
- **Day 5**: Initial validation and bug fixes

### Week 2: Enforcement Systems  
- **Day 1-2**: Implement file placement validation engine
- **Day 3-4**: Deploy workflow mode monitoring
- **Day 5**: Integration testing and refinement

### Week 3: Monitoring Framework
- **Day 1-2**: Create compliance tracking system
- **Day 3-4**: Implement performance dashboard
- **Day 5**: Generate baseline compliance metrics

### Week 4: Optimization
- **Day 1-3**: Refine validation logic based on real usage
- **Day 4-5**: Performance optimization and documentation

## Success Metrics and KPIs

### Primary Metrics:
1. **File Placement Accuracy**: Target 100% compliance
2. **Task Interpretation Accuracy**: Target 100% correct verb interpretation
3. **Workflow Mode Adherence**: Target 100% compliance with supervised mode
4. **Guideline Discovery Rate**: Target <30 seconds to locate relevant guidelines

### Secondary Metrics:
1. **Violation Reduction**: Target 90% reduction in violations within 4 weeks
2. **Time to Compliance**: Target <5 minutes for full A2G guideline review
3. **Error Prevention**: Target 95% prevention of repeat violations

## Risk Assessment

### High Risk:
- **AI agents may resist new protocols**: Mitigation through clear error messages and enforced validation
- **Performance impact from validation**: Mitigation through optimized checking algorithms

### Medium Risk:
- **Integration conflicts with existing workflows**: Mitigation through gradual rollout and testing
- **False positives in validation**: Mitigation through comprehensive test cases

### Low Risk:
- **User resistance to new procedures**: Mitigation through clear documentation and benefits communication

## Expected Outcomes

1. **100% A2G Compliance**: AI agents consistently follow all A2G guidelines
2. **Eliminated Common Violations**: No more root-level file placement or premature implementation
3. **Improved Task Execution**: Clear distinction between planning and implementation phases
4. **Enhanced Monitoring**: Real-time visibility into AI agent compliance
5. **Reduced Manual Intervention**: Automated validation reduces need for manual correction

## Conclusion

This implementation plan addresses the root causes of AI agent non-compliance through systematic intervention at multiple levels. By making A2G guideline consultation mandatory and automatic, we eliminate the procedural gaps that currently allow violations to occur.

The phased approach ensures minimal disruption while maximizing compliance improvement, with comprehensive monitoring to measure success and identify areas for continued optimization.
