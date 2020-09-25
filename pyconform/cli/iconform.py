#! /usr/bin/env python
"""
PyConform - Command-Line Interface

This command-line tool creates the

COPYRIGHT: 2017-2020, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import argparse
import json
import os
import sys
import uuid

from pyconform import miptableparser

version = "v20190309"

# Map netcdf types to python types
data_types = {
    "char": "char",
    "byte": "byte",
    "short": "short",
    "int": "int",
    "float": "float",
    "real": "real",
    "double": "double",
    "character": "char",
    "integer": "int",
}

# The way the date should be formatted in the filenames
date_strings = {
    "1hr": "_{%Y%m%d%H%M-%Y%m%d%H%M}",
    "1hrCM": "_{%Y%m%d%H%M-%Y%m%d%H%M}-clim",
    "1hrPt": "_{%Y%m%d%H%M-%Y%m%d%H%M}",
    "3hr": "_{%Y%m%d%H%M-%Y%m%d%H%M}",
    "3hrPt": "_{%Y%m%d%H%M-%Y%m%d%H%M}",
    "6hr": "_{%Y%m%d%H%M-%Y%m%d%H%M}",
    "6hrPt": "_{%Y%m%d%H%M-%Y%m%d%H%M}",
    "day": "_{%Y%m%d-%Y%m%d}",
    "dec": "_{%Y-%Y}",
    "fx": "",
    "mon": "_{%Y%m-%Y%m}",
    "monC": "_{%Y%m-%Y%m}-clim",
    "monPt": "_{%Y%m-%Y%m}",
    "subhrPt": "_{%Y%m%d%H%M-%Y%m%d%H%M}",
    "yr": "_{%Y-%Y}",
    "yrPt": "_{%Y-%Y}",
}


def parseArgs(argv=None):

    desc = "This tool creates a specification file that is needed to run PyConform."

    parser = argparse.ArgumentParser(prog="createOutputSpecs", description=desc)
    parser.add_argument(
        "-d",
        "--defFile",
        default=None,
        type=str,
        help="A file listing the variable definitions.",
        required=True,
    )
    parser.add_argument(
        "-g",
        "--globalAttrFile",
        default=None,
        type=str,
        help="A file listing the global attributes that " "are common to all files.",
    )
    parser.add_argument(
        "-e", "--exp", default="None", type=str, help="The name of the experiment."
    )
    parser.add_argument(
        "-m",
        "--mip",
        default="None",
        type=str,
        help="The name of the MIPs to generate spec files for",
    )
    parser.add_argument(
        "-t",
        "--miptables",
        default="None",
        type=str,
        help="The name of the MIP Tables to generate spec files for",
    )
    parser.add_argument(
        "-tt",
        "--mipTableType",
        default="xml",
        type=str,
        help="MIP table file type.  Can be xml, cmor, or excel.",
    )
    parser.add_argument(
        "-u",
        "--userList",
        default=None,
        type=str,
        help="A file containing cf-compliant names to derive.",
    )
    parser.add_argument(
        "-o",
        "--outputpath",
        default=os.getcwd(),
        type=str,
        help="Output pathname for the output specification file(s).",
    )
    parser.add_argument(
        "-p",
        "--outdir",
        default=os.getcwd(),
        type=str,
        help="Output pathname for the conformer output files(s). This will be appended to each output file.",
    )
    parser.add_argument(
        "-to",
        "--testoutput",
        default=False,
        type=bool,
        help="Create test output for xconform.",
    )

    return parser.parse_args(argv)


def load(defs, key=None):

    def_dict = {}
    ig_dict = {}
    if key == "ga":
        def_dict[key] = {}
        ig_dict[key] = {}
    for line in defs:
        input_glob = None
        line = line.strip()
        # hanle comments
        if "#" in line:
            if "TABLE" in line:
                key = line.split(":")[1].strip()
                def_dict[key] = {}
                ig_dict[key] = {}
            if "Coords" in line:
                key = "Coords_" + line.split(":")[1].strip()
                def_dict[key] = {}
                ig_dict[key] = {}
            if len(line.split("#")) == 2:
                input_glob = line.split("#")[1]
            line = line.split("#")[0].strip()
        # slit definition into the two parts
        split = line.split("=")
        if len(split) >= 2:
            if key == "ga" and split[1] == "":
                def_dict[key][split[0].strip()] = "__FILL__"
                ig_dict[key][split[0].strip()] = input_glob
            else:
                ig_dict[key][split[0].strip()] = input_glob
                if len(split) == 2:
                    def_dict[key][split[0].strip()] = split[1].strip()
                else:
                    def_dict[key][split[0].strip()] = "=".join(split[1:]).strip()
        else:
            if len(line) > 0:
                print("Could not parse this line: ", line)

    if key == "ga":
        return def_dict
    else:
        return def_dict, ig_dict


def fill_missing_glob_attributes(attr, table, v, grids):

    for a, d in attr.items():
        if d is not None:
            if "__FILL__" in d:
                if "activity_id" in a and "activity_id" in table:
                    attr["activity_id"] = table["activity_id"]
                elif "creation_date" in a:
                    attr["creation_date"] = ""
                elif "data_specs_version" in a and "data_specs_version" in table:
                    attr["data_specs_version"] = table["data_specs_version"]
                elif "experiment" in a and "experiment" in table:
                    attr["experiment"] = table["experiment"]
                elif "external_variables" in a:
                    if "cell_measures" in v.keys():
                        if "areacello" in v["cell_measures"]:
                            if (
                                "external_variables" not in attr.keys()
                                or "FILL" in attr["external_variables"]
                            ):
                                attr["external_variables"] = "areacello"
                            else:
                                attr["external_variables"] = (
                                    attr["external_variables"] + " areacello"
                                )
                        if "areacella" in v["cell_measures"]:
                            if (
                                "external_variables" not in attr.keys()
                                or "FILL" in attr["external_variables"]
                            ):
                                attr["external_variables"] = "areacella"
                            else:
                                attr["external_variables"] = (
                                    attr["external_variables"] + " areacella"
                                )
                        if "areacellr" in v["cell_measures"]:
                            if (
                                "external_variables" not in attr.keys()
                                or "FILL" in attr["external_variables"]
                            ):
                                attr["external_variables"] = "areacellr"
                            else:
                                attr["external_variables"] = (
                                    attr["external_variables"] + " areacellr"
                                )
                        if "areacellg" in v["cell_measures"]:
                            if (
                                "external_variables" not in attr.keys()
                                or "FILL" in attr["external_variables"]
                            ):
                                attr["external_variables"] = "areacellg"
                            else:
                                attr["external_variables"] = (
                                    attr["external_variables"] + " areacellg"
                                )
                        if "volcello" in v["cell_measures"]:
                            if (
                                "external_variables" not in attr.keys()
                                or "FILL" in attr["external_variables"]
                            ):
                                attr["external_variables"] = "volcello"
                            else:
                                attr["external_variables"] = (
                                    attr["external_variables"] + " volcello"
                                )

                elif "frequency" in a:
                    attr["frequency"] = v["frequency"]
                elif "realm" in a and "realm" in v.keys():
                    attr["realm"] = v["realm"]
                elif "table_id" in a:
                    attr["table_id"] = v["mipTable"]
                elif "tracking_id" in a:
                    attr["tracking_id"] = "hdl:21.14100/" + str(uuid.uuid4())
                elif "variable_id" in a and "variable_id" in v.keys():
                    attr["variable_id"] = v["variable_id"]

    if "FILL" in attr["external_variables"]:
        attr.pop("external_variables")

    if "branch_method" in attr.keys():
        if "no parent" not in attr["branch_method"]:
            if "branch_time_in_child" in attr.keys():
                if len(attr["branch_time_in_child"]) > 0:
                    try:
                        attr["branch_time_in_child"] = float(
                            attr["branch_time_in_child"].split("D")[0]
                        )
                    except ValueError:
                        attr["branch_time_in_child"] = attr[
                            "branch_time_in_child"
                        ].split("D")[0]
            if "branch_time_in_parent" in attr.keys():
                if len(attr["branch_time_in_parent"]) > 0:
                    try:
                        attr["branch_time_in_parent"] = float(
                            attr["branch_time_in_parent"].split("D")[0]
                        )
                    except ValueError:
                        attr["branch_time_in_parent"] = attr[
                            "branch_time_in_parent"
                        ].split("D")[0]
            if "parent_mip_era" in attr.keys() and len(attr["parent_activity_id"]) > 2:
                attr["parent_mip_era"] = attr["mip_era"]
            else:
                attr["parent_mip_era"] = "no parent"
            if (
                "parent_source_id" in attr.keys()
                and len(attr["parent_activity_id"]) > 2
            ):
                attr["parent_source_id"] = attr["source_id"]
            else:
                attr["parent_source_id"] = ""
            if (
                "parent_time_units" in attr.keys()
                and len(attr["parent_activity_id"]) > 2
            ):
                attr["parent_time_units"] = "days since 0001-01-01 00:00:00"
            else:
                attr["parent_time_units"] = "none"
        else:
            if "branch_time_in_child" in attr.keys():
                attr["branch_time_in_child"] = float(
                    attr["branch_time_in_child"].split("D")[0]
                )
            if "branch_time_in_parent" in attr.keys():
                attr["branch_time_in_parent"] = 0.0
            if "parent_mip_era" in attr.keys():
                attr["parent_mip_era"] = "no parent"
            if "parent_source_id" in attr.keys():
                attr["parent_source_id"] = "no parent"
            if "parent_time_units" in attr.keys():
                attr["parent_time_units"] = "no parent"

    else:
        if "branch_time_in_child" in attr.keys():
            attr["branch_time_in_child"] = "no parent"
        if "branch_time_in_parent" in attr.keys():
            attr["branch_time_in_parent"] = "no parent"
        if "parent_mip_era" in attr.keys():
            attr["parent_mip_era"] = "no parent"
        if "parent_source_id" in attr.keys():
            attr["parent_source_id"] = "no parent"
        if "parent_time_units" in attr.keys():
            attr["parent_time_units"] = "no parent"

    if "variant_label" in attr.keys():
        pre = attr["variant_label"].split("r")[1]
        attr["realization_index"] = int(pre.split("i")[0])
        pre = pre.split("i")[1]
        attr["initialization_index"] = int(pre.split("p")[0])
        pre = pre.split("p")[1]
        attr["physics_index"] = int(pre.split("f")[0])
        pre = int(pre.split("f")[1])
        attr["forcing_index"] = int(pre)

    if "further_info_url" in attr.keys():
        url_ok = True
        if "__FILL__" in attr["further_info_url"]:
            if "mip_era" in attr.keys():
                mip_era = attr["mip_era"]
            else:
                mip_era = ""
                url_ok = False
            if "institution_id" in attr.keys():
                institution_id = attr["institution_id"]
            else:
                institution_id = ""
                url_ok = False
            if "source_id" in attr.keys():
                source_id = attr["source_id"]
            else:
                source_id = ""
                url_ok = False
            if "experiment_id" in attr.keys():
                experiment_id = attr["experiment_id"]
            else:
                experiment_id = ""
                url_ok = False
            if "sub_experiment_id" in attr.keys():
                sub_experiment_id = attr["sub_experiment_id"]
            else:
                sub_experiment_id = ""
            if "variant_label" in attr.keys():
                ripf = attr["variant_label"]
            else:
                ripf = ""
                url_ok = False
            if url_ok:
                info_url = "{0}.{1}.{2}.{3}.{4}.{5}".format(
                    mip_era,
                    institution_id,
                    source_id,
                    experiment_id,
                    sub_experiment_id,
                    ripf,
                )
                attr["further_info_url"] = "https://furtherinfo.es-doc.org/" + info_url
    if "grid" in attr.keys():
        if len(attr["realm"]) > 0:
            attr["grid"] = grids[attr["realm"].split()[0]]
        else:
            attr["grid"] = "CAN NOT FIND GRID - NO REALM IN DATAREQ"

    return attr


def defineVar(v, varName, attr, table_info, definition, ig, experiment, out_dir):

    v2 = dict(v)
    for key, value in v.items():  # remove all attributes that do not have values
        if value == "":
            v2.pop(key, None)

    attributes = dict(attr)

    if "grids" in attributes.keys():
        p1 = attributes["grids"].split(";")
        grids = {}
        for p in p1:
            g = p.split(":")[1]
            for model in p.split(":")[0].split(","):
                grids[model.strip()] = g
    attributes.pop("grids", None)

    attributes = fill_missing_glob_attributes(attributes, table_info, v, grids)

    # Get variables needed to piece together the filename
    ripf_list = [
        "realization_index",
        "initialization_index",
        "physics_index",
        "forcing_index",
    ]
    if all(ripf in attributes for ripf in ripf_list):
        ripf = "r{0}i{1}p{2}f{3}".format(
            str(attributes["realization_index"]),
            str(attributes["initialization_index"]),
            str(attributes["physics_index"]),
            str(attributes["forcing_index"]),
        )
    else:
        ripf = ""
    if len(ripf) < 1:
        ripf = "None"
    if "mip_era" in attributes.keys():
        mip_era = attributes["mip_era"]
    else:
        mip_era = ""
    if "activity_id" in attributes.keys():
        activity_id = attributes["activity_id"]
    else:
        activity_id = ""
    if "__FILL__" in activity_id:
        activity_id = "None"
    if "institution_id" in attributes.keys():
        institution_id = attributes["institution_id"]
    else:
        institution_id = ""
    if "source_id" in attributes.keys():
        source_id = attributes["source_id"]
    else:
        source_id = ""
    if "grid_label" in attributes.keys():
        grid = attributes["grid_label"]
    else:
        grid = ""
    # if 'sub_experiment_id' in attributes.keys():
    #     sub_experiment_id = attributes['sub_experiment_id']
    # else:
    #     sub_experiment_id = ''
    if "--ALL--" in experiment:
        experiment = "None"

    f_format = attributes["netcdf_type"]
    valid_formats = [
        "NETCDF4",
        "NETCDF4_CLASSIC",
        "NETCDF3_CLASSIC",
        "NETCDF3_64BIT_OFFSET",
        "NETCDF3_64BIT_DATA",
    ]
    if f_format not in valid_formats:
        print(
            "ERROR: ",
            f_format,
            " is not a valid format.  Please choose from ",
            valid_formats,
        )
        sys.exit(-9)
    attributes.pop("netcdf_type", None)

    if "NETCDF4" in f_format:
        if "compression" in attributes.keys():
            compression = attributes["compression"]
            attributes.pop("compression", None)
        else:
            compression = None

        if "shuffle" in attributes.keys():
            shuffle = attributes["shuffle"]
            attributes.pop("shuffle", None)
        else:
            shuffle = None
    else:
        compression = None
        shuffle = None

    # Put together the filename
    mipTable = v["mipTable"]
    if v["frequency"] in date_strings.keys():
        dst = date_strings[v["frequency"]]
    else:
        dst = ""
    vid = v["variable_id"]

    f_name = "{0}/{1}/{2}/{3}/{4}/{5}/{6}/{7}/{8}/{9}/{10}/{11}_{12}_{13}_{14}_{15}_{16}{17}.nc".format(
        out_dir,
        mip_era,
        activity_id,
        institution_id,
        source_id,
        experiment,
        ripf,
        mipTable,
        vid,
        grid,
        version,
        vid,
        mipTable,
        source_id,
        experiment,
        ripf,
        grid,
        dst,
    )
    var = {}

    # Remove any __FILL__ values in attributes
    for a in attributes.keys():
        if isinstance(attributes[a], str):
            if "__FILL__" in attributes[a]:
                attributes[a] = ""

    # put together the dictionary entry for this variable
    var["attributes"] = v2
    var["definition"] = definition
    if ig:
        var["input_glob"] = ig
    var["file"] = {}
    var["file"]["attributes"] = attributes
    var["file"]["attributes"]["variant_label"] = ripf
    var["attributes"]["comment"] = definition
    var["file"]["filename"] = f_name
    var["file"]["format"] = f_format
    if compression is not None:
        var["file"]["compression"] = compression
    if shuffle is not None:
        var["file"]["shuffle"] = shuffle

    if (
        "type" in v.keys()
        and v["type"] != "None"
        and v["type"] != ""
        and v["type"] is not None
    ):
        var["datatype"] = data_types[v["type"]]
    else:
        var[
            "datatype"
        ] = "real"  # This is done because some of the variables in the request have no type listed yet

    #### Needed to get working with netcdf4_classic and netcdf3_classic
    #    if 'type' in v.keys() and v['type'] != 'None' and v['type'] != '' and v['type'] != None:
    #        if 'real' in data_types[v['type']]:
    #            var["datatype"]  = "float"
    #        else:
    #            var["datatype"]  = data_types[v['type']]
    #    else:
    #        var["datatype"] = 'float' #  This is done because some of the variables in the request have no type listed yet

    if "requested" in v.keys():
        if v["requested"] != "":
            var["definition"] = v["requested"]
    if "coordinates" in v.keys():
        var["dimensions"] = list(reversed(v["coordinates"].split("|")))
        var["attributes"]["coordinates"] = " ".join(
            list(reversed(v["coordinates"].split("|")))
        )
        # var["attributes"].pop('coordinates')
    else:
        var["dimensions"] = []

    # return the variable dictionary with all pieces added
    return var


def defineAxes(v, name):

    # define the axes that is used by at least one of the variables in the file

    var = {}
    v2 = dict(v)

    # remove all of the attributes that have no values
    for key, value in v.items():
        if value == "":
            v2.pop(key, None)
    # Hardcode this value in for time.  Not ideal, but the request has it listed as "days since ?" and this will fail.
    if "time" in name:
        v2["units"] = "days since 0001-01-01 00:00:00"

    # put everything into a variable dictionary
    var["attributes"] = v2
    if "type" in v.keys():
        var["datatype"] = data_types[v["type"]]
    if "requested" in v.keys():
        if v["requested"] != "":
            try:
                req = [float(val) for val in v["requested"].split()]
            except ValueError:
                req = v["requested"].split()
            except AttributeError:
                req = v["requested"]
            if len(req) > 0:
                var["definition"] = req
            # var['definition'] =  v['requested']
    var["dimensions"] = [name]

    # return the variable dictionary with all pieces added
    return var


def getUserVars(fn):

    # create variables from a list supplied by the user

    variables = []
    with open(fn) as f:
        for vr in f:
            vr = vr.strip()
            if vr != "":
                variables.append(vr)

    return variables


def create_output(
    exp_dict,
    definitions,
    input_glob,
    attributes,
    output_path,
    args,
    experiment,
    out_dir,
    testoutput,
):

    # create the output json files

    TableSpec = {}
    AllMissing = {}

    # go through each one of the data requests from the experiments
    for t, table_dict in exp_dict.items():

        ReqSpec = {}
        variables = {}
        axes = {}
        table_info = {}

        AllMissing[t] = []

        # separate the data request
        variables = table_dict["variables"]
        axes = table_dict["axes"]
        table_info = table_dict["table_info"]
        # attributes.update(table_info)
        if "generic_levels" in table_info.keys():
            g_levels = table_info["generic_levels"]
            g_split = g_levels.split(" ")
            for i in g_split:
                axes[i] = {}

        # identifier = t
        var_list = {}

        # For each variable in the definition file, create a file entry in the spec and define it
        for v, d in variables.items():
            ts_key = None
            mip = d["mipTable"]
            if mip in definitions.keys():
                ig = ""
                if v in definitions[mip].keys():
                    v_def = definitions[mip][v]
                    ig = input_glob[mip][v]
                    var_list[v] = defineVar(
                        d, v, attributes, table_info, v_def, ig, experiment, out_dir
                    )
                    realm = d["realm"].replace(" ", "_")
                    ts_key = (
                        var_list[v]["file"]["attributes"]["activity_id"]
                        + "_"
                        + var_list[v]["attributes"]["mipTable"]
                        + "_"
                        + realm
                    )
                    if ts_key not in TableSpec.keys():
                        TableSpec[ts_key] = {}
                    TableSpec[ts_key][
                        var_list[v]["file"]["attributes"]["variable_id"]
                    ] = var_list[v]
                    t_realm = "NoRealm"
                    for k1, v1 in definitions.items():
                        if "Coords" in k1:
                            if k1.split("_")[1] in realm:
                                t_realm = k1.split("_")[1].strip()
                    for dim in var_list[v]["dimensions"]:
                        if (
                            dim not in TableSpec[ts_key].keys()
                            and dim != ""
                            and dim != "None"
                        ):
                            TableSpec[ts_key][dim] = defineAxes(axes[dim], dim)
                            if "Coords_" + t_realm in definitions.keys():
                                if dim in definitions["Coords_" + t_realm].keys():
                                    if "landUse" in dim:
                                        TableSpec[ts_key][dim]["definition"] = [
                                            0,
                                            1,
                                            2,
                                            3,
                                        ]
                                    else:
                                        TableSpec[ts_key][dim][
                                            "definition"
                                        ] = definitions["Coords_" + t_realm][dim]
                                else:
                                    if (
                                        "definition"
                                        not in TableSpec[ts_key][dim].keys()
                                    ):
                                        print(
                                            "MISSING "
                                            + dim
                                            + " in "
                                            + "Coords_"
                                            + t_realm
                                            + " (for variable "
                                            + v
                                            + ")"
                                        )
                else:
                    print("missing:", v)
            else:
                AllMissing[t].append(v)

        ReqSpec["variables"] = var_list

    # create json files per MIP+table
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if not testoutput:
        for n, t in TableSpec.items():
            f = output_path + "/" + experiment + "_" + n + "_spec.json"
            with open(f, "w") as outfile:
                json.dump(t, outfile, sort_keys=True, indent=4)
    else:
        ignore = [
            "latitude",
            "longitude",
            "olevel",
            "plev19",
            "time",
            "time1",
            "alevhalf",
            "ygre",
            "xgre",
            "vegtype",
            "spectband",
            "areacellg",
            "alevel",
            "xant",
            "yant",
            "rho",
            "tau",
            "plev3",
            "gridlatitude",
            "plev39",
            "plev4",
            "plev27",
            "plev3",
            "plev7h",
            "plev7c",
            "plev8",
            "plev7h",
            "sdepth",
            "siline",
            "basin",
            "olevel",
            "site",
            "soilpools",
            "snowdepth",
            "snowband",
            "vegtype",
            "lat",
            "lon",
            "lev",
        ]
        for n, t in TableSpec.items():
            for vn, var in t.items():
                if vn not in ignore:
                    varD = {}
                    varD[vn] = var
                    for d in var["dimensions"]:
                        varD[d] = t[d]
                    f = (
                        output_path
                        + "/"
                        + experiment
                        + "_"
                        + n
                        + "_"
                        + vn
                        + "_spec.json"
                    )
                    with open(f, "w") as outfile:
                        json.dump(varD, outfile, sort_keys=True, indent=4)


def create_non_mip_output(variables, definitions, outputpath):

    vs = {}
    missing = []
    spec = {}
    if "file_suffix" in definitions.keys():
        fn_prefix = definitions["file_suffix"]
    else:
        fn_prefix = ""
    if "output_path" in definitions.keys():
        output_path = definitions["output_path"]
    else:
        output_path = os.getcwd()

    for v in variables:
        var = v.split(":")
        vn = var[0]
        if vn in definitions.keys():
            vs[vn] = {}
            vs[vn]["definition"] = definitions[vn]
            if len(var) > 1:
                vs[vn]["dimensions"] = var[1].split(".")
            vs[vn]["filename"] = output_path + "/" + vn + "_" + fn_prefix + ".nc"
            # get the dimensions
            for d in vs[vn]["dimensions"]:
                if d not in vs.keys():
                    vs[d] = {}
                    vs[d]["definition"] = definitions[d]
                    vs[d]["dimensions"] = d
        else:
            missing.append(vn)
    spec["variables"] = vs
    spec["variables_missing_defs"] = missing

    # Write output json file
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

    f = outputpath + "/user_defined.json"
    with open(f, "w") as outfile:
        json.dump(spec, outfile, sort_keys=True, indent=4)


def main(argv=None):

    args = parseArgs(argv)

    print("\n")
    print("------------------------------------------")
    print("Running createOutputSpecs with these args:\n")
    print("Variable Definitions: ", args.defFile)
    print("Global Attributes to be added to each file: ", args.globalAttrFile)
    print("Experiment Name: ", args.exp)
    print("MIPs: ", args.mip)
    print("MIP Tables: ", args.miptables)
    print("MIP Table Type: ", args.mipTableType)
    print("User supplied variable list: ", args.userList)
    print("Will create output spec files within this directory:", args.outputpath)
    print("------------------------------------------")

    # Open/Read the definition file
    if os.path.isfile(args.defFile):
        with open(args.defFile) as y_definitions:
            definitions, input_glob = load(y_definitions)
    else:
        print("Definition file does not exist: ", args.defFile)
        os.sys.exit(1)

    # Open/Read the global attributes file
    attributes = {}
    if args.globalAttrFile:
        for gaFile in args.globalAttrFile.split(","):
            if os.path.isfile(gaFile):
                if "json" in gaFile:
                    print("opening ", gaFile)
                    with open(gaFile) as gaF:
                        ga = json.load(gaF)
                    for k in ga.keys():
                        if ga[k] is None:
                            ga[k] = ""
                    attributes.update(ga)
                else:
                    with open(gaFile) as y_attributes:
                        attributes = load(y_attributes, key="ga")["ga"]
            else:
                if args.globalAttrFile and not os.path.isfile(args.globalAttrFile):
                    print(
                        "Global Attributes file does not exist: "
                    ), args.globalAttrFile
                    os.sys.exit(1)

    # Open/Read the MIP table
    exps = args.exp.split(",")
    if exps[0] == "None":
        exps = ["--ALL--"]
    mips = args.mip.split(",")
    if mips[0] == "None":
        mips = ["--ALL--"]
    tables = args.miptables.split(",")
    if tables[0] == "None":
        tables = ["--ALL--"]

    # dq = dreq.loadDreq()
    # if '--ALL--' in exps:
    #     exps = dq.inx.experiment.label.keys()

    # Go through a user supplied list if specified
    variables = []
    if args.userList and os.path.isfile(args.userList):
        variables = getUserVars(args.userList)
    else:
        if args.userList and not os.path.isfile(args.userList):
            variables = args.userList.split(",")

    if "None" in args.mipTableType.capitalize():
        create_non_mip_output(variables, definitions, args.outputpath)
    else:
        for exp in exps:
            exp_dict = miptableparser.mip_table_parser(
                exp, mips, tables, variables, type=args.mipTableType
            )

            if len(exp_dict.keys()) > 0:
                # Write the spec files out to disk
                create_output(
                    exp_dict,
                    definitions,
                    input_glob,
                    attributes,
                    args.outputpath,
                    args,
                    exp,
                    args.outdir,
                    args.testoutput,
                )


if __name__ == "__main__":
    main()
