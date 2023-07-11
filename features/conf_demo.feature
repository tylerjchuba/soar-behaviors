Feature: Basic Proxy Block Service
        Scenario: Blocked Artifacts are tagged as 'blocked' without '.'
            Given the container "Proxy block request with a single blocked domain" under the label "workbench"
            Given the artifact "blocked domain" labeled "event"
                  | destinationDnsDomain | blockeddomain.com |
             Then the container and artifacts are created
             Then the playbook "triage_blocked_domains" is ran
              And the results are collected
             Then the artifact "blocked domain" has the "tags" of "[blocked]"
              And the playbook "triage_blocked_domains" has the status of "success"
            
        Scenario: Blocked Artifacts are tagged as 'blocked' without '.'
            Given the container "Proxy block request with a single blocked domain" under the label "workbench"
            Given the artifact "blocked domain" labeled "event"
                  | destinationDnsDomain | .blockeddomain.com |
             Then the container and artifacts are created
             Then the playbook "triage_blocked_domains" is ran
              And the results are collected
             Then the artifact "blocked domain" has the "tags" of "[blocked]"
              And the playbook "triage_blocked_domains" has the status of "success"
            
        
        Scenario Outline: Testing known blocked domains
            Given the container "Proxy block with a single domain" under the label "workbench"
            Given the artifact "blocked domain" labeled "event"
              And the artifact "blocked domain" has the "cef" of "destinationDnsDomain:<domain>"
             Then the container and artifacts are created
             Then the playbook "triage_blocked_domains" is ran
              And the results are collected
             Then the artifact "blocked domain" has the "tags" of "<tags>"
              And the playbook "triage_blocked_domains" has the status of "success"
            
        Examples:
                  | domain            | tags      |
                  | blockeddomain.com | []        |
                  | .random.com       | [blocked] |

        @ignore_exception
        Scenario Outline: Non-blocked are commented on the container
            Given the container "Proxy block with a single domain" under the label "workbench"
            Given the artifact "blocked domain" labeled "event"
              And the artifact "blocked domain" has the "cef" of "destinationDnsDomain:<domain>"
             Then the container and artifacts are created
             Then the playbook "triage_blocked_domains" is ran
              And the results are collected
             Then the artifact "blocked domain" has the "tags" of "<tags>"
              And "<domain> is currently not blocked" is commented

        Examples:
                  | domain      | tags |
                  | .google.com | []   |
                  | .splunk.com | []   |