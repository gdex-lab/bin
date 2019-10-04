import re

def format_single(field_name):
  s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field_name)
  s1 = re.sub('([0-9])([a-z])', r'\1_\2', s1)
  s1 = re.sub('([a-z])([0-9])', r'\1_\2', s1)
  return re.sub('([a-z])([A-Z])', r'\1_\2', s1).lower()

def is_verified_string_field(message_name, field_name):
  string_fields = [
    "Initials.value",
    "LocationDescription.value",
    "LiabilityIndicator.value",
    "OverallStatus.value",
    "NumberOfEmployees.value",
    "Title.value",
    "CompanyOwnsership.value",
    "CorpStatusCode.value",
    "AccountComments.value",
    "PaymentRating.value",
    "PreviousAccountReference.value",
    "AccountReference.value",
    "ProductCode.value",
    "Reject.value",
    "ReasonCode.value",
    "AnnualSalesRange.value",
  ]
  for sf in string_fields:
    names = sf.split(".")
    if message_name == names[0] and field_name == names[1]:
      return True
  return False

def format_leaf(field_name, message_name):
  field_name = format_single(field_name)

  # make string default type
  pb_type = "string"
  
  if is_verified_string_field(message_name, field_name):
    return pb_type + " " + field_name

  elif field_name == "value" or \
    "num_" in field_name or \
    field_name.startswith("count_") or \
    field_name.startswith("years_") or \
    field_name.startswith("number_"):

    pb_type = "int64"
  
  return pb_type + " " + field_name

def format_repeated(field_name):
  field_name = format_single(field_name)
  if field_name.endswith("s"):
    return field_name
  return field_name + "s"

def format_repeated_leaf(field_name, message_name):
  field_name = format_leaf(field_name, message_name)
  return format_repeated(field_name)

def read_jellyfish_output(filename):
  with open(filename) as f:
        content = f.readlines()

  unique_messages = {}
  top_level_objs = {}
  for line in content:
    # break each line out by period separators
    # e.g. Site.IdTrait.AddressTrait\n becomes ["Site", "IDTrait", "AddressTrait\n"]
    messages = line.split(".")

    # treat top-level objects special
    top_level_objs[messages[0]] = 0

    # at this point we have a list like [UltimateParent, IdTrait, AddressTrait, TraitActivity, DateCreated\n]
    # each list item needs a unique object, except the last item
    # any parent items need a reference to the item immediatly following
    for idx, message in enumerate(messages):

      # if message not already present in unique messages, and it's a a parent object, create an entry
      if message not in unique_messages.keys() and not "\n" in message:
        unique_messages[message] = {}

      # if it's not a leaf node, append the subitem as a value for the message
      # e.g. ["Site", "IDTrait", "AddressTrait\n"] will become {Site: {IDTrait}}, {IDTrait: {AddressTrait}}
      if not "\n" in message:
        unique_messages[message][messages[idx + 1]] = {}
  return unique_messages, top_level_objs

def write_top_level(top_level_objs, f):
  # work on top-level object
  root_fields = ""
  for idx, field in enumerate(top_level_objs.keys()):
    repeated = False
    leaf = False

    if "[]" in field:
      repeated = True
      field = field.replace("[]", "")

    elif "\n" in field:
      leaf = True
      field = field.replace("\n", "")

    if repeated and leaf: # I don't think we have any of these yet
      root_fields += "\n  repeated string {} = {};".format(format_repeated_leaf(field, "x"), idx + 5)
    elif repeated and not leaf:
      root_fields += "\n  repeated {} {} = {};".format(field, format_repeated(field), idx + 5)
    elif not repeated and leaf:
      root_fields += "\n  string {} = {};".format(format_leaf(field, "x"), idx + 5)
    elif not repeated and not leaf:
      root_fields += "\n  {} {} = {};".format(field, format_single(field), idx + 5)

  # write top-level report message
  root_object = """message ReportResponse {{
    nav.Header header = 1;
    google.protobuf.Timestamp created_at = 3;
    string uuid = 4;{}
  }}\n""".format(root_fields)
  f.write(root_object)

def write_sub_messages(unique_messages, f):
  # generate code for lower-level protobuf messages, assuming all string types for now
  for m in unique_messages:
    fields = ""
    for idx, field in enumerate(unique_messages[m].keys()):
      leaf = False
      repeated = False

      # if it's a leaf field, set the flag
      if "\n" in field:
        leaf = True
        field = field.replace("\n", "")
      
      # if it's a repeated (list) field, set the flag
      if "[]" in field:
        repeated = True
        field = field.replace("[]", "")

      # generate the appropriate code to represent the field
      if leaf and repeated:
        fields += "\n  repeated {} = {};".format(format_repeated_leaf(field, m), idx + 1)
      elif leaf and not repeated:
        fields += "\n  {} = {};".format(format_leaf(field, m), idx + 1)
      elif not leaf and repeated:
        fields += "\n  repeated {} {} = {};".format(field, format_repeated(field), idx + 1)
      elif not leaf and not repeated:
        fields += "\n  {} {} = {};".format(field, format_single(field), idx + 1)


    obj = "message {} {{{}\n}}\n".format(m.replace("[]", ""), fields)
    f.write(obj)
  f.close()

def main():
  # use filename to point to file with jellyfish data
  filename = "/Users/grant/Repos/protorepo/nav/pudge/reports/equifax/business_v2_editor.proto"
  unique_messages, top_level_objs = read_jellyfish_output(filename)

  # write results (overwrite) to file named like original with .gen appended to end
  f = open(filename + ".gen", "w")
  write_top_level(top_level_objs, f)
  write_sub_messages(unique_messages, f)

if __name__ == "__main__":
  main()